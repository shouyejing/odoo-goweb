# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

{
 'name': 'Import Supplier Pricelist Data',
 'version': '0.1',
 'author': 'Cozy Business Solutions Pvt.Ltd.',
 'category': 'Data Migration',
 'description': """
Import Supplier Pricelist
==================================

 -> Add following parameters to 'System Parameters'
   - Key = pricelist_url
   - Value = Full path of the directory containing csv files e.g. (/home/software/workspace/odoo/openerp/supplier_pricelist)
""",
 'depends': ['purchase', 'sale','account','procurement_jit'],
 'demo': [],
 'data': ['supplier_cron.xml','partner_view.xml','email_template_data.xml'],
 'test': [],
 'installable': True,
 'auto_install': False,
}
