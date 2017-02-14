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

{
    'name': "BPD TXT File Generator",

    'summary': """
        Generacion Archivo TXT Nomina Banco Popular D.
        """,

    'description': """
        Este modulo permite generar un archivo TXT para el envio de la nomina electronica al Banco BPD.
    """,

    'author': "Open Business Solutions SRL.",
    'website': "http://",


    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll', 'l10n_custom_do_hr_payroll'],

    # always loaded
    'data': [
        'hr_payslip_run_view.xml',
        'secuencia.xml',
        'res_partner_bank_ext.xml',
#        'security/bpd_payroll_txt_file_security.xml',

    ],
    # 'js': ['static/src/js/ipf.js'],
    #'qweb': ['static/src/xml/marcos_ncf.xml'],
    # only loaded in demonstration mode
    # 'demo': [
    # ],
}
