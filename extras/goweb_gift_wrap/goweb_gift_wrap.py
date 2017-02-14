# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Smile (<http://www.smile.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.tools import ustr
from openerp.tools.translate import _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    add_gift_message = fields.Boolean(string="Añadir un mensaje de regalo a mi pedido",  )
    gift_from = fields.Char(string="De", required=False, )
    gift_to = fields.Char(string="Para", required=False, )
    gift_message = fields.Text(string="Mensaje", required=False, )
    gift_wrap_true = fields.Boolean(string="Envoltura de Regalo",  )
    additional_message = fields.Text(string="Mensaje Adicional", required=False, )
    time_of_delivery = fields.Char(string="Fecha y Hora de Envio", required=False, )

    @api.multi
    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        for order in self:
            order.picking_ids.write({
                    'add_gift_message': order.add_gift_message,
                    'gift_from': order.gift_from,
                    'gift_to': order.gift_to,
                    'gift_message': order.gift_message,
                    'gift_wrap_true': order.gift_wrap_true,
                    'additional_message': order.additional_message,
                    'time_of_delivery': order.time_of_delivery,
            })
        return res

class SaleOrder(models.Model):
    #_name = 'sale_order.gift_wrap'
    _inherit = 'sale.order'

    add_gift_message = fields.Boolean(string="Añadir un mensaje de regalo a mi pedido",  )
    gift_from = fields.Char(string="De", required=False, )
    gift_to = fields.Char(string="Para", required=False, )
    gift_message = fields.Text(string="Mensaje", required=False, )
    gift_wrap_true = fields.Boolean(string="Envoltura de Regalo",  )
    additional_message = fields.Text(string="Mensaje Adicional", required=False, )
    time_of_delivery = fields.Char(string="Fecha y Hora de Envio", required=False, )

    @api.model
    def _prepare_procurement_group(self, order):
        res = super(SaleOrder, self)._prepare_procurement_group(order)
        res.update({'add_gift_message': order.add_gift_message,
                    'gift_from': order.gift_from,
                    'gift_to': order.gift_to,
                    'gift_message': order.gift_message,
                    'gift_wrap_true': order.gift_wrap_true,
                    'additional_message': order.additional_message,
                    'time_of_delivery': order.time_of_delivery,
                    })
        return res


class ResPartner(models.Model):

    _inherit = 'res.partner'

    contact_name = fields.Char(string="Contacto", required=False, )

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    add_gift_message = fields.Boolean(string="Añadir un mensaje de regalo a mi pedido",  )
    gift_from = fields.Char(string="De", required=False, )
    gift_to = fields.Char(string="Para", required=False, )
    gift_message = fields.Text(string="Mensaje", required=False, )
    gift_wrap_true = fields.Boolean(string="Envoltura de Regalo",  )
    additional_message = fields.Text(string="Mensaje Adicional", required=False, )
    time_of_delivery = fields.Char(string="Fecha y Hora de Envio", required=False, )

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    add_gift_message = fields.Boolean(related='group_id.add_gift_message')
    gift_from = fields.Char(related='group_id.gift_from')
    gift_to = fields.Char(related='group_id.gift_to')
    gift_message = fields.Text(related='group_id.gift_message')
    gift_wrap_true = fields.Boolean(related='group_id.gift_wrap_true')
    additional_message = fields.Text(related='group_id.additional_message')
    time_of_delivery = fields.Char(related='group_id.time_of_delivery')

    @api.model
    def create_procurement_purchase_order(self,
                                          procurement,
                                          po_vals,
                                          line_vals):
        po_vals.update({'add_gift_message': procurement.add_gift_message,
                        'gift_from': procurement.gift_from,
                        'gift_to': procurement.gift_to,
                        'gift_message': procurement.gift_message,
                        'gift_wrap_true': procurement.gift_wrap_true,
                        'additional_message': procurement.additional_message,
                        'time_of_delivery': procurement.time_of_delivery,
                        })
        _super = super(ProcurementOrder, self)
        return _super.create_procurement_purchase_order(procurement,
                                                        po_vals,
                                                        line_vals)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    add_gift_message = fields.Boolean(string="Añadir un mensaje de regalo a mi pedido",  )
    gift_from = fields.Char(string="De", required=False, )
    gift_to = fields.Char(string="Para", required=False, )
    gift_message = fields.Text(string="Mensaje", required=False, )
    gift_wrap_true = fields.Boolean(string="Envoltura de Regalo",  )
    additional_message = fields.Text(string="Mensaje Adicional", required=False, )
    time_of_delivery = fields.Char(string="Fecha y Hora de Envio", required=False, )
