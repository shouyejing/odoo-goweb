# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

{
    'name': 'Magento Stock Comparision',
    'version': '2.0.0',
    'category': 'MOB : Maintenance Module',
     'sequence': 1,
    'summary': 'Customize MOB',
    'description': """
1. MOB : Maintenance Module--Magento Stock Comparision(MOB Stock Comparision)
=============================================================================

This Module helps in maintaining stock between openerp and magento with real time.

You can easily make out all unmatched product stock crossponding to magento stock,
along with their appropriate details.

This module works very well with latest version of magento 1.9.* and Odoo 8.0
------------------------------------------------------------------------------
	""",
	'author' : 'Webkul Software Pvt Ltd.',
	'website' : 'http://www.webkul.com',
	'depends' : ['magento_bridge'],
	'data' : [
				'data/mob_stock_compare_cron.xml',
				'data/mob_stock_server_actions.xml',
				'wizard/stock_wizard_view.xml',
				'product_stock_view.xml'
				],
	'installable': True,
	'auto_install': False,	
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: