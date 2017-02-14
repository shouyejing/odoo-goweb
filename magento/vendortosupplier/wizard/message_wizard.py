# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###################################################################################


from openerp.osv import fields, osv
from openerp.tools.translate import _
	
class message_wizard(osv.osv_memory):
	_name = "message.wizard"

	_columns={
			'text': fields.text('Message' ,readonly=True ,translate=True),
	         }

message_wizard()