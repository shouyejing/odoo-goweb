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

class supplier_configure(osv.osv):
	_name = "supplier.configure"
	_inherit = ['mail.thread']
	_description = "Supplier Configuration"

	def _default_instance_name(self, cr, uid, context=None):
		if context is None:
			context = {}
		res = self.pool.get('ir.sequence').get(cr, uid, 'supplier.configure')
		return res

	_columns = {
		'name': fields.char('Supplier Name', size=255),
		'url': fields.char("Supplier Url", size=64, required=True),
		'user':fields.char('Supplier User Name', required=True, size=100),
		'pwd':fields.char('Supplier Password', required=True, size=100),
		'db':fields.char('Supplier DataBase', required=True, size=100),
		'supplier_uid':fields.integer('Supplier User', readonly=True),
		'partner_id':fields.many2one('res.partner', 'Preferred Supplier'),
		'status':fields.char('Connection Status', readonly=True, size=255),
		'active':fields.boolean('Active'),
		'validate':fields.boolean('Validate', readonly=True),
		'credential':fields.boolean('Show/Hide Credentials Tab', 
							help="If Enable, Credentials tab will be displayed, "
							"And after filling the details you can hide the Tab."),
		'create_date':fields.datetime('Created Date'),
	}

	_defaults = {
		'credential':True,
		'active':lambda *a: 1,	
		'name':_default_instance_name,
		}


	#############################################
	##    		Supplier connection		   	   ##
	#############################################
	def test_connection(self, cr, uid, ids, context=None):
		session = 0
		status = 'Supplier Connection Un-successful'
		text = 'Test connection Un-successful please check the supplier api credentials!!!'
		obj = self.browse(cr, uid, ids[0])
		sock_common = xmlrpclib.ServerProxy (obj.url +'/xmlrpc/common')
		supplier_uid = sock_common.login(obj.db, obj.user, obj.pwd)
		if supplier_uid:
			self.write(cr, uid, ids[0], {'supplier_uid':supplier_uid}, context)
			text = "Test Connection with supplier is successful"
			status = "Congratulation, It's Successfully Connected with Supplier Api."
		res_model = 'message.wizard'
		partial = self.pool.get('message.wizard').create(cr, uid, {'text':text})
		if not obj.validate:
			partial = self.pool.get('supplier.wizard').create(cr, uid, {'supplier_token_key':False})
			res_model = 'supplier.wizard'
		self.write(cr, uid, ids[0],{'status':status})
		return { 
				'name':_("Information"),
				'view_mode': 'form',
				'view_id': False,
				'view_type': 'form',
				'res_model': res_model,
				'res_id': partial,
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'new',
				'domain': '[]',
			 }


supplier_configure()
