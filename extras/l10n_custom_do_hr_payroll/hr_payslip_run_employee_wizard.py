# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_payslip_run_employee_wizard(osv.osv_memory):

    _name = 'payment.order.create'
    _description = 'payment.order.create'
    _columns = {
        'duedate': fields.date('Due Date', required=True),
        'entries': fields.many2many('account.move.line', 'line_pay_rel', 'pay_id', 'line_id', 'Entries')
    }
    _defaults = {
         'duedate': lambda *a: time.strftime('%Y-%m-%d'),
    }