# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

import xmlrpclib
from openerp.osv import fields, osv
from openerp.tools.translate import _

	
class supplier_wizard(osv.osv_memory):
	_name = "supplier.wizard"

	_columns = {
		'supplier_token_key':fields.char('Supplier Token Key')			
	}

	def buttun_validate(self, cr, uid, ids, context=None):
		status = 'Supplier Connection Un-successful'
		text = 'Test connection Un-successful please check the supplier api credentials!!!'
		context = dict(context or {})
		if context.has_key('active_id'):
			if ids:
				config_obj = self.pool.get('supplier.configure').browse(cr, uid, context['active_id'], context)
				wizard_obj = self.browse(cr, uid, ids[0], context)
				supplier_obj = xmlrpclib.ServerProxy(config_obj.url+'/xmlrpc/object')
				validate = supplier_obj.execute(config_obj.db, config_obj.supplier_uid, config_obj.pwd, 'vendor.configure', 'search', [('token_key','=', wizard_obj.supplier_token_key)])
				if not validate:
					self.pool.get('supplier.configure').write(cr, uid, context['active_id'], {'supplier_uid':False, 'validate':False}, context)
				else:
					self.pool.get('supplier.configure').write(cr, uid, context['active_id'], {'validate':True}, context)
					text = "Test Connection with supplier is successful"
					status = "Congratulation, It's Successfully Connected with Supplier Api."
		
			self.pool.get('supplier.configure').write(cr, uid, context['active_id'], {'status':status})		
		partial = self.pool.get('message.wizard').create(cr, uid, {'text':text})
		return { 'name': ("Information"),
				 'view_mode': 'form',
				 'view_type': 'form',
				 'res_model': 'message.wizard',
				 'view_id': False,
				 'res_id': partial,
				 'type': 'ir.actions.act_window',
				 'nodestroy': True,
				 'target': 'new',
			 }

		
