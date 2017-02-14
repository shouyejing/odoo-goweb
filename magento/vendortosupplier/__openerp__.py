# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###################################################################################

{
    'name': 'Supplier Vendor Bridge',
    'version': '1.0.0',
    'category': 'Generic Modules',
    'sequence': 1,
    'author': 'Webkul Software Pvt. Ltd.',
	'website': 'http://www.webkul.com',
    'summary': 'Basic SVB',
    'description': """

Supplier Vendor Bridge (SVB)
=========================

This Brilliant Module will Connect Vendor with Supplier and synchronise Data. 
--------------------------------------------------------------------------


Some of the brilliant feature of the module:
--------------------------------------------

	
	1. synchronise all the order(Invoice, shipping) Status to Supplier.
	
This module works very well with latest version Odoo 8.0
------------------------------------------------------------------------------
    """,
	'depends': [
				'magento_bridge',
			],
	'data': [
				'wizard/supplier_wizard_view.xml',
				'wizard/message_wizard_view.xml',
				'views/connection_view.xml',
				'views/svb_sequence.xml'
				],
	'application': True,
	'installable': True,
	'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
