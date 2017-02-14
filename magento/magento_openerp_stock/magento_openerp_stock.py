 # -*- coding: utf-8 -*-
##############################################################################
#		
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 webkul
#	 Author :
#				www.webkul.com	
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import xmlrpclib

from openerp.addons.magento_bridge.mob import XMLRPC_API
import logging
_logger = logging.getLogger(__name__)

################## .............magento-Odoo stock.............##################

class stock_move(osv.osv):
	_inherit="stock.move"

	def action_done(self, cr, uid, ids, context=None):
		""" Process completly the moves given as ids and if all moves are done, it will finish the picking.
		"""
		if context is None:
			context = {}
		context = dict(context)
		res = super(stock_move, self).action_done(cr, uid, ids, context)
		if not context.has_key('stock_from'):
			for id in ids:
				data = self.browse(cr, uid, id)
				erp_product_id = data.product_id.id
				flag = 2
				if data.origin and data.origin.startswith('SO'):
					flag = 1 # no origin
				product_qty = 0
				warehouse_id = 0
				if flag == 1:
					product_qty = int(data.product_qty)
					if 'OUT' in data.picking_id.name:
						product_qty = int(-product_qty)
						warehouse_id = data.warehouse_id.id
				if flag == 2:
					check_in = self.pool.get('stock.warehouse').search(cr,uid,[('lot_stock_id','=',data.location_dest_id.id),('company_id','=',data.company_id.id)],limit=1)
					if check_in:
						# Getting Goods.
						warehouse_id = check_in[0]
						product_qty = int(data.product_qty)
					check_out = self.pool.get('stock.warehouse').search(cr,uid,[('lot_stock_id','=',data.location_id.id),('company_id','=',data.company_id.id)],limit=1)
					if check_out:
						# Sending Goods.
						warehouse_id = check_out[0]
						product_qty = int(-data.product_qty)
				
				context['warehouse'] = warehouse_id
				self.check_warehouse(cr, uid, erp_product_id, warehouse_id, product_qty, context)
		return res

	def check_warehouse(self, cr, uid, erp_product_id, warehouse_id, product_qty, context=None):
		mapping_ids = self.pool.get('magento.product').search(cr, uid, [('pro_name','=',erp_product_id)])
		if mapping_ids:
			mapping_obj = self.pool.get('magento.product').browse(cr, uid, mapping_ids[0])
			instance_id = mapping_obj.instance_id.id
			mage_product_id = mapping_obj.mag_product_id
			if mapping_obj.instance_id.warehouse_id.id == warehouse_id:					
				self.synch_quantity(cr, uid, mage_product_id, erp_product_id, instance_id, context)
			

	def synch_quantity(self, cr, uid, mage_product_id, erp_product_id, instance_id, context=None):
		response = self.update_quantity(cr, uid, mage_product_id, erp_product_id, instance_id, context)
		if response[0]==1:
			return True
		else:
			self.pool.get('magento.sync.history').create(cr,uid,{'status':'no','action_on':'product','action':'c','error_message':response[1]})
		
	def update_quantity(self, cr, uid, mage_product_id, erp_product_id, instance_id, context=None):
		qty = 0		
		text = ''
		stock = 0
		session = False
		if mage_product_id:
			obj = self.pool.get('magento.configure').browse(cr, uid, instance_id)		
			if not obj.active :
				return [0,' Connection needs one Active Configuration setting.']
			else:
				url = obj.name + XMLRPC_API
				user = obj.user
				pwd = obj.pwd
				try:
					server = xmlrpclib.Server(url)
					session = server.login(user,pwd)
				except xmlrpclib.Fault, e:
					text = 'Error, %s Magento details are Invalid.'%e
				except IOError, e:
					text = 'Error, %s.'%e
				except Exception,e:
					text = 'Error in Magento Connection.'
				if not session:
					return [0,text]
				else:
					try:
						total_quantity = self.pool.get('product.product').browse(cr, uid, erp_product_id, context).qty_available							
						if total_quantity > 0:
							stock = 1						
						update_data = [[mage_product_id,{'manage_stock':1, 'qty':total_quantity,'is_in_stock':stock}]]
						server.call(session, 'magerpsync.update_product_stock', update_data)
						return [1, '']
					except Exception,e:
						return [0,' Error in Updating Quantity for Magneto Product Id %s.'%mage_product_id]
		else:
			return [1, 'Error in Updating Stock, Magento Product Id Not Found!!!']
stock_move()	