# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd
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
from openerp.osv import fields as old_fields,osv
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_compare, float_round

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    @api.model
    def _get_product_supplier(self, procurement):
        return self.env['res.partner'].search([('name','=', procurement.product_id.preferred_supplier),('supplier','=',True)])
    
    
class purchase_order(models.Model):
    _inherit = 'purchase.order'
      
    @api.model    
    def _prepare_order_line_move(self, order, order_line, picking_id, group_id):
        res = super(purchase_order,self)._prepare_order_line_move(order, order_line, picking_id, group_id)
        for vals in res:
            product = vals.has_key('product_id') and vals['product_id']
            type = self.env['product.product'].browse(product).type
            if vals.has_key('location_id') and type == 'product':
                vals['location_id'] = order.picking_type_id.default_location_src_id.id
        return res
      
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.multi
    def action_confirm(self):
        stock_todo = {}
        for line in self:
            if line.product_id.type == 'product':
                supplier = self.env['res.partner'].search([('name','=', line.product_id.preferred_supplier),('supplier','=',True)]).name
                if not stock_todo.has_key(supplier):
                    stock_todo.update({supplier:{}})
                if not stock_todo[supplier].has_key(line.product_id):
                    stock_todo[supplier].update({line.product_id:0.0})
                stock_todo[supplier].update({line.product_id:line.product_qty})
        if stock_todo:
            self.env['import.supplier.pricelist'].set_stock_default_warehouse(stock_todo, True)
        return super(purchase_order_line,self).action_confirm()
            
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def action_done(self):
        res = super(sale_order, self).action_done()
        template = self.env.ref('account.email_template_edi_invoice', False)
        if self.invoiced and template:
            for invoice in self.invoice_ids:
                template.send_mail(invoice.id, force_send=True)
        return res
    
    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        vals = super(sale_order, self)._prepare_order_line_procurement(order, line, group_id=group_id)
        if line.product_id.preferred_supplier and  line.product_id.type == 'product':
            warehouse = self.env['stock.warehouse'].search([('name','ilike',line.product_id.preferred_supplier)])
            vals['warehouse_id'] = warehouse and warehouse.id or False
        return vals


class stock_quant(models.Model):
    _inherit = 'stock.quant'
    
    @api.model
    def _quant_create(self, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False):  
        positive_quant = super(stock_quant, self)._quant_create(qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False)
        if move.location_id.usage == 'supplier':
            price_unit = self.env['stock.move'].get_price_unit(move)
            negative_vals = {
                             'product_id': positive_quant.product_id.id,
                             'history_ids': [(4, move.id)],
                             'in_date': positive_quant.in_date,
                             'company_id': positive_quant.company_id.id,
                             'lot_id': positive_quant.lot_id.id,
                             'owner_id': positive_quant.owner_id.id,
                             }
            rounding = move.product_id.uom_id.rounding
            negative_vals['location_id'] = force_location_from and force_location_from.id or move.location_id.id
            negative_vals['qty'] = float_round(-qty, precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.env['stock.quant'].sudo().create(negative_vals)
            positive_quant.write({'propagated_from_id': negative_quant_id.id})
        return positive_quant

class product_product(osv.osv):
    _inherit = "product.product"
    
    
    def create(self, cr, uid, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = vals['default_code'].strip()
        return super(product_product,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = vals['default_code'].strip()
        return super(product_product,self).write(cr, uid, ids, vals, context)
    
    def _get_domain_locations(self, cr, uid, ids, context=None):
        if context is None: context = {}
        magento_connection = self.pool.get('magento.configure').search(cr, uid, [], context=context)
        default_stock_location = self.pool.get('magento.configure').browse(cr, uid, magento_connection,context).location_id
        ctx = context.copy()
        ctx.update({'location':default_stock_location.id})
        return super(product_product, self)._get_domain_locations(cr, uid, ids, context=ctx)
        
class product_template(osv.osv):
    _inherit = "product.template"
    
    def create(self, cr, uid, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = vals['default_code'].strip()
        return super(product_template,self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = vals['default_code'].strip()
        return super(product_template,self).write(cr, uid, ids, vals, context)
    
    preferred_supplier =  fields.Char(string='Preferred Supplier')
    

       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
