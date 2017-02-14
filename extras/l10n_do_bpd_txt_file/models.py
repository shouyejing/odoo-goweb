# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Open Business Solutions, SRL.
#    Write by Ernesto Mendez (tecnologia@obsdr.com)
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

from openerp.osv import osv, fields
import base64
from openerp.tools.translate import _
import time
from openerp import tools
import pdb
from openerp.exceptions import Warning
import os

#_logger = logging.getLogger(__name__)

class bpd_payroll_report(osv.Model):
    _name = 'bdp.payslip.run.report'
    _description = 'Extraccion Archivo TXT Nomina Banco BPD'

    def _line_count(self, cr, uid, ids, context=None):
        bpd_payslip_run_obj = self.pool.get('bdp.payslip.run.report')
        payslip_run_report = bpd_payslip_run_obj.browse(cr, uid, ids, context=context)[0]
        return len(payslip_run_report.payslip_run_line_report_ids)

    def _get_updated_fields(self, cr, uid, ids, context=None):
        vals = {}
        vals['company_id'] = 1
        vals['line_count'] = self._line_count(cr, uid, ids, context=context)
        return vals

    _columns = {
        #'name': fields.char('Nombre'),
        'company_id': fields.many2one('res.company', u'Compañia', required=True),
        'payslip_run_id': fields.many2one('hr.payslip.run', u'Lote de Nomina', required=True,),
        'line_count': fields.integer(u"Total de registros", readonly=True),
        'report': fields.binary(u"Reporte", readonly=True),
        #'subsidiary_id': fields.many2one('res.company.subsidiary', 'Subsidiaria', required=True, readonly=True),
        'report_name': fields.char(u"Nombre de Reporte", 40, readonly=True),
        'payslip_run_line_report_ids': fields.one2many('bpd.payslip.run.line.report', 'payslip_run_report_id', u'Lineas'),
        'state': fields.selection((('draft','Pendiente'),('sent','Enviado'),('cancel','Cancel')), 'State', readonly=True),

        'type' : fields.selection((('01', 'Nomina Automatica'), ('02', 'Pago Suplidores'), ('03', 'Cobros Automaticos'), 
                                    ('04', 'Pago Prestamo'), ('05', 'Pago Tarjeta'), ('06', 'Transferencia a Cta.')), default='01', string='Tipo de Servicio'),
        'effective_date': fields.date('Fecha Efectiva', help='Fecha Futura cuando  se aplicaran los pagos', required=True),
        'numero_afiliacion': fields.char('Numero de Afiliacion', help='Numero de Afiliacion a CARDNAT'),
        'email': fields.char('Email', 40,help='Correo Electronico para recibir archivo y reporte del fin del proceso'),
        'num_cuenta': fields.integer('Numero de Cuenta', digits=1, help='Cuenta que la empresa usara para DB/CR [1/9]'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'state': 'draft',
        }

    def create(self, cr, uid, values, context=None):

        res = super(bpd_payroll_report, self).create(cr, uid, values, context=context)

        # Loads all purchases
        self.create_payslip_run_line(cr, uid, res, values['payslip_run_id'], context=context)

        # Update readonly fields
        vals = self._get_updated_fields(cr, uid, [res], context=None)
        self.write(cr, uid, [res], vals)
        return res

    def re_create_payslip_run_line(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get('bpd.payslip.run.line.report')
        report = self.browse(cr, uid, ids[0])
        line_ids = [line.id for line in report.payslip_run_line_report_ids]
        lines_obj.unlink(cr, uid, line_ids)

        result = self.create_payslip_run_line(cr, uid, report.id, report.payslip_run_id.id, context=context)

        vals = self._get_updated_fields(cr, uid, ids, context=None)
        self.write(cr, uid, ids, vals)

        return result

    def create_payslip_run_line(self, cr, uid, payslip_run_report_id, payslip_run_id, context=None):
  
        #payslip_run_id = self.browse(cr, uid, payslip_run_id)
        hr_payslip_obj = self.pool.get('hr.payslip')
        hr_payslip_run_obj = self.pool.get('hr.payslip.run')
        hr_payslip_line_obj = self.pool.get('hr.payslip.line')
        bpd_payslip_run_line_obj = self.pool.get('bpd.payslip.run.line.report')
        hr_salary_rule_category_obj = self.pool.get('hr.salary.rule.category')

        #draft_payslip_ids = hr_payslip_obj.search(cr, uid, [("state", "not in", ["draft", "verify", "cancel"]),("payslip_run_id", "=", payslip_run_id)])
        draft_payslip_ids = hr_payslip_obj.search(cr, uid, [("state", "in", ["draft", "verify", "cancel"]),("payslip_run_id", "=", payslip_run_id)])
        #if draft_payslip_ids:
        #    raise osv.except_osv(_(u'Nominas en Borrador o en Espera de Verificacion!'), _(u"Asegúrese que todas las nominas de este lote esten validadas."))

        payslip_ids = hr_payslip_obj.search(cr, uid, [("state", "in", ["done",'draft']),("payslip_run_id", "=", payslip_run_id)])
        #category_id = hr_salary_rule_category_obj.search

        sequence = 1
        line = 1
        warnings = 0
        names = []
        
        for payslip_id in payslip_ids:
            payslip = hr_payslip_obj.browse(cr, uid, payslip_id)
            if payslip.employee_id.bank_account_id:
                continue
            if not payslip.employee_id.bank_account_id:
                name = str(payslip.employee_id.name).decode("utf-8") + ' ' + str(payslip.employee_id.first_lastname).decode("utf-8") + ' ' + str(payslip.employee_id.second_lastname).decode("utf-8")
                
                names.append(name)
            #raise Warning(_('Error !'), _('Uno o algunos de los empleados en esta nomina no posee cuenta bancaria asignada. Por favor revise!'), names)        
            #else:
            #    pass

        #if names:
        #    raise Warning(_('Error !'), _('Uno o algunos de los empleados en esta nomina no posee cuenta bancaria asignada. Por favor revise!'), names)

        for payslip_id in payslip_ids:

            payslip = hr_payslip_obj.browse(cr, uid, payslip_id)            
            #if not payslip.employee_id.bank_account_id:
            #    name = str(payslip.employee_id.names) + ' ' + str(payslip.employee_id.first_lastname) + ' ' + str(payslip.employee_id.second_lastname)
            #    raise Warning(_('Error !'), _('Uno o algunos de los empleados en esta nomina no posee cuenta bancaria asignada. Por favor revise!'), name)

            slip_ids = hr_payslip_line_obj.search(cr, uid, [("slip_id", "=", payslip.id),("category_id.code","=","NET")])

            LEYENDA = 'Pago'
            MONTO = 0.00
            num_cuenta = str(payslip.employee_id.bank_account_id.acc_number)
            acc_number0 = str(num_cuenta.replace('-', ''))
            acc_number1 = str(acc_number0)[:7] + '-' + str(acc_number0)[7:]
            acc_number2 = str(acc_number1)[:11] + '-' + str(acc_number0)[10:]

            for slip_line in hr_payslip_line_obj.browse(cr, uid, slip_ids):
                MONTO += slip_line.amount

            values = {

                #u'NUM_CUENTA':payslip.employee_id.bank_account_id.acc_number,
                u'NUM_CUENTA': acc_number2,
                u'NOMBRE': payslip.employee_id.name,
                u'SECUENCIA': sequence,
                u'MONTO': abs(MONTO),
                u'LEYENDA': LEYENDA,
                u'line': line,
                u'payslip_run_report_id': payslip_run_report_id
            }

            sequence += 1
            line += 1

            bpd_payslip_run_line_obj.create(cr, uid, values, context=context)
        #self.action_generate_txt(cr, uid, payslip_run_report_id, context=context)
        return True

    def action_generate_txt(self, cr, uid, ids, context=None):
        obj = self.pool.get('bdp.payslip.run.report').browse(cr, uid, ids)
        employee_obj = self.pool.get('hr.employee') 
        COMP = obj.company_id
        IDCOMP = COMP.vat.replace('-','').zfill(15)
        
        import datetime
        
        hoy = str(datetime.datetime.now())
        YY = hoy[:4]
        MM = hoy[5:7]
        DD = hoy[8:10]
        HH = hoy[11:13]
        MI = hoy[14:16]
        
        FULL = YY+MM+DD
                
        SEQ = self.pool.get('ir.sequence').get(cr, uid, 'bpd')
        TS = obj.type
        
        name_report = 'PE{N}{TS}{MM}{DD}{SEQ}E'.format(N='01224',TS=TS, MM=MM, DD=DD, SEQ=SEQ)
        
        
        path = '/opt/odoo/{name}.txt'.format(name=name_report)
        f = open(path,'w')
              
        #f.write('{}\r\n'.format(HEADER))
        
        #Report header
        header_obj = self.pool.get('bdp.payslip.run.report')
        header = header_obj.browse(cr, uid, ids, context=context)

        document_date_start = str(header.payslip_run_id.date_start)
        document_date_end = str(header.payslip_run_id.date_end)
        document_header = document_date_start + '_' + document_date_end

        newline = os.linesep
        
        res_obj = self.pool.get('res.partner.bank')
        
        cod_bancos = {
            'Banco Popular Dominicano': '10101070',
            'Banco Popular ': '10101070',
            'Banco de Reservas': '10101010',
            'Banco del Progreso': '10101110',
            'Banco BHD': '10101230',
            'Banco BHD Leon': '10101230',
            'Banco Leon': '10101370',
            'Banco Santa Cruz': '10101340',
            'Citibank': '10101060',
            'Scotiabank': '10101030',
            'BDI': '10101360',
            'Banco Lope de Haro': '10101390',
            'Banco Vimeca': '10101380',
            'Banco Promerica': '44405900',
            'Asociacion Popular de Ahorros y Prestamos': '47940900',
            'Banco Caribe': '10101350',      
        }
        
        
        # Report Detail Lines
        CC = 0  # Cantidad Credito 
        MC = 0  # Monto Credito
        lines = ''  # Almacena todas las lineas para hacer un solo WRITE al archivo
        for line in header.payslip_run_line_report_ids:
            emp_id = employee_obj.search(cr, uid, [('name','=like', line.NOMBRE)])
            emp = employee_obj.browse(cr, uid, emp_id)
            
            ced = emp.identification_id
            pasap = emp.passport_id
            
            TD = {
                'ID': ced if ced else pasap if pasap else '0'.zfill(15),
                'TIPO': 'CE' if ced else 'PS' if pasap else 'OT'
            }
            
            bnk = emp.bank_account_id.bank_name
            digi_bnk = emp.bank_account_id.bank_check_digit
            CODBNK = cod_bancos[bnk] if bnk in cod_bancos else cod_bancos['Banco Popular Dominicano']
            cod_ope = emp.bank_account_id.cod_operation
            tipo_cuenta = emp.bank_account_id.tipo_cuenta
            moneda = emp.bank_account_id.moneda
            
            
            CC += 1
            MC += line.MONTO 
            
            CUENTAD = str(line.NUM_CUENTA).replace('-','').zfill(20)
            name     = str(line.NOMBRE).upper()
            SECTRANS = str(line.SECUENCIA).zfill(7)
            MONTO = str('%.2f' % line.MONTO).replace('.','').zfill(13)
            legend = str(line.LEYENDA)
                        
            line = "N{IDCOMP}{SEC}{SECTRANS}{CUENTAD}{TipoCuenta}{MONEDA}{CODBNK}{DIGIBNK}{CODOP}{MONTO}{TIPOID}{ID}{NOMBRE}".format(
                IDCOMP=IDCOMP, 
                SEC=SEQ, 
                SECTRANS=SECTRANS,
                CUENTAD=CUENTAD, 
                TipoCuenta=tipo_cuenta,
                MONEDA=moneda, 
                CODBNK=CODBNK, 
                DIGIBNK=digi_bnk, 
                CODOP=cod_ope,
                MONTO=MONTO, 
                TIPOID=TD['TIPO'],
                ID=TD['ID'].replace('-', '').zfill(15),
                NOMBRE=emp.name,
            )
            
            lines += line + '\r\n'
            #f.write('{}\r\n'.format(line))
        HEADER = 'H{RNC}{NOMCOMP}{SEC}{TIPOSERV}{FECEFECT}{CD}{MD}{CC}{MC}{NAFILIA}{FEC}{HOR}{EMAIL}{CUENTA}'.format(
             RNC=IDCOMP, NOMCOMP=COMP.name, SEC=SEQ, TIPOSERV=obj.type, FECEFECT=obj.effective_date.replace('-',''),
             CD='0'.zfill(11), MD='0'.zfill(13), CC=str(CC).zfill(11), MC=str(MC).replace('.','').zfill(13), 
             NAFILIA=obj.numero_afiliacion or '0'.zfill(15), FEC=FULL, HOR=HH+MI, EMAIL=obj.email, CUENTA=obj.num_cuenta,
             )
 
        f.write('{}\r\n'.format(HEADER))
        f.write(lines)
        
        f.close()

        f = open(path,'rb')
        report = base64.b64encode(f.read())
        f.close()
        report_name = name_report +  '.txt'
        self.write(cr, uid, ids, {'report': report, 'report_name': report_name})
        return True

class bpd_payroll_report_line(osv.Model):
    _name = 'bpd.payslip.run.line.report'
    _order = 'line'

    _columns = {
        u'line': fields.integer(u'Linea'),
        u'NUM_CUENTA': fields.char(u'Numero de Cuenta', 13, required=False),
        u'NOMBRE': fields.char(u'Nombre Beneficiario', required=False),
        u'SECUENCIA': fields.integer(u'Secuencia', required=False),
        u'MONTO': fields.float(u'Monto a Pagar'),
        u'LEYENDA': fields.char(u'Leyenda'),
        u'payslip_run_report_id': fields.many2one('bdp.payslip.run.report')

    }
