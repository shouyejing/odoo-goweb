# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###################################################################################

import xmlrpclib
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import logging
_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
	_inherit = "purchase.order"

	def wkf_confirm_order(self, cr, uid, ids, context=None):
		res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)		
		order_line = []
		purchase_order_obj = self.browse(cr, uid, ids[0], context)
		order_line_objs = purchase_order_obj.order_line
		origin = purchase_order_obj.name
		supplier_name = purchase_order_obj.partner_id.name
		supplier_pool = self.pool.get('supplier.configure')
		config_ids = supplier_pool.search(cr, uid, [('active','=',True),('partner_id','=', purchase_order_obj.partner_id.id)])
		if config_ids:
			config_obj = supplier_pool.browse(cr, uid, config_ids[0])
			supplier_id = config_obj.partner_id.id
			if supplier_id != purchase_order_obj.partner_id.id:
				return res
				
			for order_line_obj in order_line_objs:
				order_line_data = {}
				order_line_data['name'] = order_line_obj.name
				order_line_data['default_code'] = order_line_obj.product_id.default_code
				order_line_data['product_uom_qty'] = order_line_obj.product_qty
				order_line_data['default_code'] = order_line_obj.product_id.default_code
				order_line_data['price_unit'] = order_line_obj.price_unit
				order_line.append(order_line_data)

			try:
				supplier_obj = xmlrpclib.ServerProxy(config_obj.url+'/xmlrpc/object')
				order_name = supplier_obj.execute(config_obj.db, config_obj.supplier_uid, config_obj.pwd, 'sale.order', 'create_order', config_obj.supplier_uid, origin, order_line)				
				if order_name:
					purchase_order_obj.message_post(body="<b>New Sale Order " + order_name + " has been successfully created at " + supplier_name + " odoo. </b>")
			except Exception, e:
				_logger.info("Sales Order %r not created at puntomac due to %r", e)
				return res
		return res

class stock_move(osv.osv):
	_inherit="stock.move"

	def create_move_line(self, cr, uid, default_code, product_qty, context=None):
		if context is None:
			context = {}
		product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', default_code)])
		if product_ids:
			location_id = 0
			product_obj = self.pool.get('product.product').browse(cr, uid, product_ids[0], context)
			location_dest_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Inventory loss')])
			instance_ids = self.pool.get('magento.configure').search(cr, uid, [('active', '=', True)])
			if instance_ids:
				location_id = self.pool.get('magento.configure').browse(cr, uid, instance_ids[0]).location_id.id
				if location_dest_ids:
					move_data = {
								'product_id':product_obj.id,
								'name':product_obj.name,
								'product_uom':product_obj.uom_id.id or 1,
								'product_uom_qty':product_qty,
								'location_id':location_id,
								'location_dest_id':location_dest_ids[0]
					}
					mv_id = self.create(cr, uid, move_data, context)
					self.action_done(cr, uid, [mv_id], context=context)
		return True

class product_template(osv.osv):
	_inherit = "product.template"

	def create(self, cr, uid, vals, context=None):
		context = dict(context or {})
		vals = self.assignPreferredSupplier(cr, uid, [], vals, context)
		return super(product_template, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		context = dict(context or {})
		if isinstance(ids, (int, long)):
			ids = [ids]
		vals = self.assignPreferredSupplier(cr, uid, ids, vals, context)
		return super(product_template, self).write(cr, uid, ids, vals, context=context)

	def assignPreferredSupplier(self, cr, uid, ids, vals, context=None):
		if context.has_key('magento'):
			if vals.has_key('preferred_supplier'):
				if vals['preferred_supplier'] == "PUNTOMAC S R L":
					supplier_pool = self.pool.get('supplier.configure')
					config_ids = supplier_pool.search(cr, uid, [('active','=',True)])
					if config_ids:
						config_obj = supplier_pool.browse(cr, uid, config_ids[0])
						supplier_id = config_obj.partner_id.id
						seller_data = []
						if ids:
							seller_ids = self.pool.get('product.supplierinfo').search(cr, uid, [('product_tmpl_id','=',ids[0]), ('name','=', supplier_id)])
							if seller_ids:
								seller_data = [(6, 0, seller_ids)]
						if not seller_data:
							seller_data = [(0, 0, {'name':supplier_id, 'min_qty':0, 'delay':1})]
						vals['seller_ids'] = seller_data
		return vals
