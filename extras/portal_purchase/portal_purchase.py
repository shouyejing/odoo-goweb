# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2012 OpenERP S.A. <http://openerp.com>
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

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
import pdb

class purchase_order(osv.Model):
    _inherit = 'purchase.order'

    # make the real method inheritable
    _payment_block_proxy = lambda self, *a, **kw: self._portal_payment_block(*a, **kw)

    _columns = {
        'portal_payment_options': fields.function(_payment_block_proxy, type="html", string="Portal Payment Options"),
    }

    def wkf_confirm_order(self, cr, uid, ids, context=None):

        for this in self.browse(cr, uid, ids, context=context):
            #pdb.set_trace()
            if not this.partner_id.is_consignee:
                res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
                template = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal_purchase', 'email_template_edi_purchase_supplier_portal')[1]
                mail_id = self.pool.get('email.template').send_mail(cr, uid, template, ids[0], force_send=True)

            elif this.partner_id.is_consignee:
                res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
                template = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal_purchase', 'email_template_edi_purchase_transport_portal')[1]
                mail_id = self.pool.get('email.template').send_mail(cr, uid, template, ids[0], force_send=True)

            return res




    def _portal_payment_block(self, cr, uid, ids, fieldname, arg, context=None):
        result = dict.fromkeys(ids, False)
        payment_acquirer = self.pool['payment.acquirer']
        for this in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if not (not (this.state not in ('draft', 'cancel')) or this.invoiced):
                result[this.id] = payment_acquirer.render_payment_block(
                    cr, uid, this.name, this.amount_total, this.pricelist_id.currency_id.id,
                    partner_id=this.partner_id.id, company_id=this.company_id.id, context=context)
        return result

    def wkf_send_rfq(self, cr, uid, ids, context=None):
        '''  Override to use a modified template that includes a portal signup link '''

        action_dict = super(purchase_order, self).wkf_send_rfq(cr, uid, ids, context=context)
        #pdb.set_trace()
        try:
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'email_template_edi_purchase_portal')[1]
            # assume context is still a dict, as prepared by super
            ctx = action_dict['context']
            ctx['default_template_id'] = template_id
            ctx['default_use_template'] = True
        except Exception:
            pass
        return action_dict

    '''
    def action_quotation_send(self, cr, uid, ids, context=None):
        Override to use a modified template that includes a portal signup link

        action_dict = super(purchase_order, self).action_quotation_send(cr, uid, ids, context=context)
        try:
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'email_template_edi_purchase_portal')[1]
            # assume context is still a dict, as prepared by super
            ctx = action_dict['context']
            ctx['default_template_id'] = template_id
            ctx['default_use_template'] = True
        except Exception:
            pass
        return action_dict
    '''

    def action_button_confirm(self, cr, uid, ids, context=None):
        # fetch the partner's id and subscribe the partner to the purchase order
        assert len(ids) == 1
        document = self.browse(cr, uid, ids[0], context=context)
        partner = document.partner_id
        if partner not in document.message_follower_ids:
            self.message_subscribe(cr, uid, ids, [partner.id], context=context)
        return super(purchase_order, self).action_button_confirm(cr, uid, ids, context=context)

    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, uid, ids[0], context=context)
        contex_signup = dict(context, signup_valid=True)
        return self.pool['res.partner']._get_signup_url_for_action(
            cr, uid, [document.partner_id.id], action='mail.action_mail_redirect',
            model=self._name, res_id=document.id, context=contex_signup,
        )[document.partner_id.id]

    def get_formview_action(self, cr, uid, id, context=None):
        user = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
        if user.share:
            document = self.browse(cr, uid, id, context=context)
            action_xmlid = 'action_quotations_portal' if document.state in ('draft', 'sent') else 'action_orders_portal'
            return self.pool['ir.actions.act_window'].for_xml_id(cr, uid, 'portal_purchase', action_xmlid, context=context)
        return super(purchase_order, self).get_formview_action(cr, uid, id, context=context)

    '''
    def action_invoice_create(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)
        template = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal_purchase', 'email_template_edi_supplier_invoice')[1]
        mail_id = self.pool.get('email.template').send_mail(cr, uid, template, ids[0], force_send=True)
        return res
    '''
    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        context = dict(context or {})

        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                #if the company of the document is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                if po_line.state == 'cancel':
                    continue
                acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)
                po_line.write({'invoice_lines': [(4, inv_line_id)]})

            # get invoice data and create invoice
            inv_data = self._prepare_invoice(cr, uid, order, inv_lines, context=context)
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice

            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)
            self.message_subscribe(cr, uid, [inv_id], [order.partner_id.id], context=context)
            #template = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal_purchase', 'email_template_edi_supplier_invoice')[1]
            #mail_id = self.pool.get('email.template').send_mail(cr, uid, template, inv_id, force_send=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]})
            res = inv_id
        return res

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    # make the real method inheritable
    _payment_block_proxy = lambda self, *a, **kw: self._portal_payment_block(*a, **kw)

    _columns = {
        'portal_payment_options': fields.function(_payment_block_proxy, type="html", string="Portal Payment Options"),
    }

    def _portal_payment_block(self, cr, uid, ids, fieldname, arg, context=None):
        result = dict.fromkeys(ids, False)
        payment_acquirer = self.pool.get('payment.acquirer')
        for this in self.browse(cr, uid, ids, context=context):
            if this.type == 'in_invoice' and this.state not in ('draft', 'done') and not this.reconciled:
                result[this.id] = payment_acquirer.render_payment_block(
                    cr, uid, this.number, this.residual, this.currency_id.id,
                    partner_id=this.partner_id.id, company_id=this.company_id.id, context=context)
        return result

    def action_invoice_sent(self, cr, uid, ids, context=None):
        '''  Override to use a modified template that includes a portal signup link '''
        action_dict = super(account_invoice, self).action_invoice_sent(cr, uid, ids, context=context)
        try:
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal_purchase', 'email_template_edi_supplier_invoice')[1]
            # assume context is still a dict, as prepared by super
            ctx = action_dict['context']
            ctx['default_template_id'] = template_id
            ctx['default_use_template'] = True
        except Exception:
            pass
        return action_dict

    def invoice_validate(self, cr, uid, ids, context=None):
        # fetch the partner's id and subscribe the partner to the invoice
        for invoice in self.browse(cr, uid, ids, context=context):
            partner = invoice.partner_id
            if partner not in invoice.message_follower_ids:
                self.message_subscribe(cr, uid, [invoice.id], [partner.id], context=context)
        return super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)

    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, uid, ids[0], context=context)
        contex_signup = dict(context, signup_valid=True)
        return self.pool['res.partner']._get_signup_url_for_action(
            cr, uid, [document.partner_id.id], action='mail.action_mail_redirect',
            model=self._name, res_id=document.id, context=contex_signup,
        )[document.partner_id.id]

    def get_formview_action(self, cr, uid, id, context=None):
        user = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
        if user.share:
            return self.pool['ir.actions.act_window'].for_xml_id(cr, uid, 'portal_purchase', 'portal_action_invoices', context=context)
        return super(account_invoice, self).get_formview_action(cr, uid, id, context=context)

'''
class mail_mail(osv.osv):
    _inherit = 'mail.mail'

    def _postprocess_sent_message(self, cr, uid, mail, context=None, mail_sent=True):
        if mail_sent and mail.model == 'purchase.order':
            po_obj = self.pool.get('purchase.order')
            order = po_obj.browse(cr, uid, mail.res_id, context=context)
            partner = order.partner_id
            # Add the customer in the PO as follower
            if partner not in order.message_follower_ids:
                po_obj.message_subscribe(cr, uid, [mail.res_id], [partner.id], context=context)
            # Add all recipients of the email as followers
            for p in mail.partner_ids:
                if p not in order.message_follower_ids:
                    po_obj.message_subscribe(cr, uid, [mail.res_id], [p.id], context=context)
        return super(mail_mail, self)._postprocess_sent_message(cr, uid, mail=mail, context=context, mail_sent=mail_sent)
'''
