#-*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
from dateutil import relativedelta
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
#coment
class hr_contract(orm.Model):
    _name='hr.contract'
    _inherit='hr.contract'

    def _get_contract_years(self, cr, uid, ids, name, arg, context=None):

        res = {}

        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = (dt2/365)
        return res

    def _get_contract_days(self, cr, uid, ids, name, arg, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = dt2
        return res

    _columns = {

        'contract_years': fields.function(_get_contract_years, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Years at Work'),
        'contract_days': fields.function(_get_contract_days, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Days at Work'),
        
        'avance_sueldo_apply': fields.boolean('Aplicar?'),
        'avance_sueldo_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'avance_sueldo_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'avance_sueldo_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'avance_sueldo_frequency_number': fields.integer('Numero de Veces'),
        'avance_sueldo_start_date': fields.date('Fecha Inicial'),
        'avance_sueldo_end_date': fields.date('Fecha Final'),

        'descuento_factura_apply': fields.boolean('Aplicar?'),
        'descuento_factura_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'descuento_factura_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'descuento_factura_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'descuento_factura_frequency_number': fields.integer('Numero de Veces'),
        'descuento_factura_start_date': fields.date('Fecha Inicial'),
        'descuento_factura_end_date': fields.date('Fecha Final'),

        'prest_cjc_apply': fields.boolean('Aplicar?'),
        'prest_cjc_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'prest_cjc_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'prest_cjc_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'prest_cjc_frequency_number': fields.integer('Numero de Veces'),
        'prest_cjc_start_date': fields.date('Fecha Inicial'),
        'prest_cjc_end_date': fields.date('Fecha Final'),

        'otros_desc_apply': fields.boolean('Aplicar?'),
        'otros_desc_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'otros_desc_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'otros_desc_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'otros_desc_frequency_number': fields.integer('Numero de Veces'),
        'otros_desc_start_date': fields.date('Fecha Inicial'),
        'otros_desc_end_date': fields.date('Fecha Final'),

        'optica_apply': fields.boolean('Aplicar?'),
        'optica_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'optica_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'optica_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'optica_frequency_number': fields.integer('Numero de Veces'),
        'optica_start_date': fields.date('Fecha Inicial'),
        'optica_end_date': fields.date('Fecha Final'),
        
        'smc_apply': fields.boolean('Aplicar?'),
        'smc_discount_amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'smc_frequency_type': fields.selection((('fixed', 'Fijo'),
                                            ('variable', 'Variable')), 'Tipo de Frecuencia'),
        'smc_apply_on': fields.selection((('1', 'Primera Quincena'),
                                      ('2', 'Segunda Quincena'),
                                      ('3', 'Primera y Segunda Quincena')), 'Aplicar en'),
        'smc_frequency_number': fields.integer('Numero de Veces'),
        'smc_start_date': fields.date('Fecha Inicial'),
        'smc_end_date': fields.date('Fecha Final'),




    }

    _defaults = {
        'avance_sueldo_frequency_type' : 'fixed',
        'descuento_factura_frequency_type' : 'fixed',
        'prest_cjc_frequency_type' : 'fixed',
        'otros_desc_frequency_type' : 'fixed',
        'optica_frequency_type' : 'fixed',
        'smc_frequency_type': 'fixed',

    }
