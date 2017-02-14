# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
import re

class marcos_ipf(models.Model):
    _name = 'ipf.printer.config'

    name = fields.Char("Descripcion", required=True)
    host = fields.Char("Host", required=True)
    user_ids = fields.Many2many('res.users', string="Usuarios")
    print_copy = fields.Boolean("Imprimir con copia", default=False)
    subsidiary = fields.Many2one("shop.ncf.config", string="Sucursal", required=True)

    def ncf_fiscal_position_exception(self, partner_name):
        raise except_orm(u'Tipo de comprobante fiscal inválido!',
                u"El tipo de comprobante no corresponde a la posicion fical del cliente '%s'!" % (partner_name))

    @api.model
    def print_done(self, values):
        id = values[0]
        nif = values[1]
        if not nif == None:
            return self.pool.get("account.invoice").write(self.env.cr, self.env.uid, id, {"nif": nif})

    @api.model
    def ipf_print(self):
        invoice = False
        if self.env.context.get("active_model", False) == "account.invoice":
            invoice = self.env["account.invoice"].browse(self.env.context.get("active_id"))
        elif self.env.context.get("active_model", False) == "pos.order" or self.env.context.get("active_model", False) == "pos.payment":
            invoice = self.env["pos.order"].browse(self.env.context.get("active_id")).invoice_id
        elif self.env.context.get("active_model", False) == "pos_order_ui":
            pos_reference = self.env.context.get("active_id")
            self.env.cr.execute("select id from pos_order where pos_reference = %s", (pos_reference,))
            pos_order_id = self.env.cr.fetchone()
            # import pdb;pdb.set_trace()
            invoice = self.env["pos.order"].search([('id','=', pos_order_id[0])]).invoice_id

        invoice_dict = {}
        printer = self.search([("user_ids", "=", self.env.uid)])
        print_copy = printer.print_copy
        subsidiary = printer.subsidiary
        ncf_type = False

        invoice_dict["type"] = "nofiscal"
        if invoice.state in ['open', 'paid'] and invoice.nif == "false":
            invoice_dict["ncf"] = invoice.number
            ncf_type = invoice.partner_id.property_account_position.fiscal_type

            if invoice.type == "out_invoice":
                if ncf_type == "gov":
                    invoice_dict["type"] = "fiscal"
                else:
                    invoice_dict["type"] = ncf_type
                    if not invoice_dict["type"]:
                        invoice_dict["type"] = "final"

            elif invoice.type == "out_refund":
                ncf_type = invoice.partner_id.property_account_position.fiscal_type or "final"
                invoice_dict["reference_ncf"] = invoice.parent_id.number
                if ncf_type == "final":
                    invoice_dict["type"] = "final_note"
                elif ncf_type in ["fiscal", "gov"]:
                    invoice_dict["type"] = "fiscal_note"
                elif ncf_type == "special":
                    invoice_dict["type"] = "special_note"

            if invoice.type == "out_invoice":
                if ncf_type == "fiscal":
                    if not invoice.number[9:-8] == "01":
                        return self.ncf_fiscal_position_exception(invoice.partner_id.name)
                elif ncf_type == "special":
                    if not invoice.number[9:-8] == "14":
                        return self.ncf_fiscal_position_exception(invoice.partner_id.name)
                elif ncf_type == "gov":
                    if not invoice.number[9:-8] == "15":
                        return self.ncf_fiscal_position_exception(invoice.partner_id.name)
                elif invoice_dict["type"] in ["final_note", "fiscal_note", "special_note"]:
                    if not invoice.number[9:-8] == "04":
                        return self.ncf_fiscal_position_exception(invoice.partner_id.name)
                elif invoice_dict["type"] == "final":
                    if not invoice.number[9:-8] == "02":
                        return self.ncf_fiscal_position_exception(invoice.partner_id.name)
        else:
            invoice_dict["type"] = "nofiscal"

        invoice_dict["copy"] = print_copy
        invoice_dict["cashier"] = self.env.uid
        invoice_dict["subsidiary"] = subsidiary.id
        invoice_dict["client"] = invoice.partner_id.name
        invoice_dict["rnc"] = invoice.partner_id.ref

        invoice_items_list = []
        for line in invoice.invoice_line:
            invoice_items_dict = {}
            # variant_name = self.pool.get("product.product").name_get(self.env.cr, self.env.uid, [line.product_id.id],
            #                                                          context=self.env.context)[0][1]
            # description = re.sub(r'^\[[\s\d]+\]\s+', '', variant_name).strip()
            description = re.sub(r'^\[[\s\d]+\]\s+', '', line.name).strip()

            description_splited = [description[x:x+21].replace("\n","") for x in range(0,len(description),21)]


            invoice_items_dict["description"] = description_splited.pop()

            if len(description_splited) > 0:
                invoice_items_dict["extra_descriptions"] = description_splited[0:9]

            extra_description = []
            # if not variant_name == line.name:
            #     extra_description += line.name.split("\n")
            if extra_description:
                invoice_items_dict["extra_description"] = extra_description[0:9]
            invoice_items_dict["quantity"] = line.quantity

            tax_id = line.invoice_line_tax_id

            if not len(tax_id) == 1:
                raise except_orm(u'Error en el impuestos de productos',
                u"Los productos de ventas no deben de tener un impuesto asignado y nunca mas de unorevise el '%s'!" % (line.name))

            tax_rate = int(tax_id.amount*100)
            tax_include = tax_id.price_include
            tax_except = tax_id.exempt

            if not tax_rate in [18, 13, 11, 8, 5, 0]:
                raise except_orm(u'Impuesto inválido',
                u"Los productos de ventas contiene un porcentaje de impuesto inválido %s" % (line.name))

            invoice_items_dict["itbis"] = tax_rate
            if tax_include or tax_except:
                invoice_items_dict["price"] = line.price_unit
            else:
                invoice_items_dict["price"] = line.price_unit*(tax_id.amount+1)

            if line.discount > 0:
                invoice_items_dict["discount"] = line.discount

            invoice_items_list.append(invoice_items_dict)


        invoice_dict["items"] = invoice_items_list

        payment_ids_list = []

        if not len(invoice.payment_ids) == 0:
            for payment in invoice.payment_ids:
                if payment.credit:
                    payment_ids_dict = {}
                    payment_ids_dict["type"] = payment.journal_id.ipf_payment_type or "other"
                    payment_ids_dict["amount"] = payment.credit
                    payment_ids_list.append(payment_ids_dict)
                else:
                    payment_ids_dict = {}
                    payment_ids_dict["type"] = payment.journal_id.ipf_payment_type or "other"
                    payment_ids_dict["amount"] = payment.debit
                    payment_ids_list.append(payment_ids_dict)
        else:
            # total = sum([l["price"]-(l["price"]*(l["discount"]/100)) for l in invoice_items_list if l.get("discount", False)]) or invoice.amount_total
            payment_ids_list.append(dict(type="other", amount=invoice.amount_total))

        if invoice_dict["type"] == "nofiscal":
            invoice_dict.update(dict(host=printer.host, invoice_id=invoice.id))
        else:
            invoice_dict.update(dict(host=printer.host, payments=payment_ids_list, invoice_id=invoice.id))
        return invoice_dict

    @api.model
    def print_precuenta(self, receipt):

        import pdb;pdb.set_trace()

