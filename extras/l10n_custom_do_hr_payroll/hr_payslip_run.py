#-*- coding: utf-8 -*-
#####
#
#Localization for payroll to the Dominican Republic.
#Modifications to the hr.payslip.run object.
#
#Author: José Ernesto Mendez @ Open Business Solutions
#
#
#####

from openerp.osv import orm, fields, osv

class hr_payslip_run (orm.Model) :

    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _columns = {
        'date_efective': fields.date('Fecha de Aplicacion', required=True,
            readonly=True, states={'draft':[('readonly', False)]}, select=True,
            help="""Date when the payment is applied. - The application date
            can't be lower than the date when the text file was sent to the
            bank."""),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency',
            required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'bank_id': fields.many2one('res.bank', 'Banco', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'sequence': fields.char('Payslip Batch Sequence', size=7,
            required=False, readonly=True, select=True, help="""Unique number
            of the payslip batch,computed automatically when the payslip batch
            is created."""),
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=True),
        'payroll_type': fields.selection([('fixed_employees', 'Empleados Fijos'),
                                          ('temporal_employees', 'Empleados Temporales'),
                                          ('probative_employees', 'Empleados Probatorios'),
                                          ('pensioner_employees', 'Pensionados'),
                                          ('commission_employees', 'Comisionistas')], 'Tipo de Nomina', required=True),
        'clave_nomina': fields.selection([('0001','0001'),
                                          ('0002','0002')], 'TSS Clave Nomina', required=True),
    }

    def _get_seq(self, cr, uid, ctx):

        seq = self.pool.get('ir.sequence').get(cr, uid, 'salary.slipbatch')
        return seq

    def _get_currency(self, cr, uid, ctx):

        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id

    def close_payslip_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    def confirm_payslips(self, cr, uid, ids, context=None):
        payslip_pool = self.pool.get('hr.payslip')
        for payslip_run in self.browse(cr, uid, ids, context=context):
            slip_ids = []
            for slip_id in payslip_run.slip_ids:
                # TODO is it necessary to interleave the calls ?
                payslip_pool.signal_workflow(cr, uid, [slip_id.id], 'hr_verify_sheet')
                payslip_pool.signal_workflow(cr, uid, [slip_id.id], 'process_sheet')
                slip_ids.append(slip_id.id)
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.payslip.run', context=c),
        'currency_id': _get_currency,
        'sequence': _get_seq,
        'clave_nomina': '0001'
    }

hr_payslip_run()

class hr_payslip(orm.Model):


    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    _columns = {
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=False),
        'payroll_type': fields.selection([('fixed_employees', 'Empleados Fijos'),
                                          ('temporal_employees', 'Empleados Temporales'),
                                          ('probative_employees', 'Empleados Probatorios'),
                                          ('pensioner_employees', 'Pensionados'),
                                          ('commission_employees', 'Comisionistas')], 'Tipo de Nomina', required=False),
        'pay_vacation': fields.boolean('Incluir Vacaciones'),
        'clave_nomina': fields.selection([('0001','0001'),
                                          ('0002','0002')], 'TSS Clave Nomina', required=True),
    }

hr_payslip()

class hr_salary_rule(orm.Model):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'

    _columns = {
        'payment_period': fields.selection((('1', 'Primera Quincena'),
                                            ('2', 'Segunda Quincena'),
                                            ('3', 'Fin de mes')), 'Periodo de Pago', required=False),
    }

