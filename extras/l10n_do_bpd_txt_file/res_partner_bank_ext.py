# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class res_partner_bank_ext(osv.Model):
    _inherit = "res.partner.bank"
    
    _columns = {
        "moneda": fields.selection((('214', 'DOP'), ('840', 'USD'),('978', 'EUR')), default='214', string='Moneda'),
        "tipo_cuenta": fields.selection((
                ('1', 'Cuenta Corriente'), ('2', 'Cuenta de Ahorros'),('3', 'Tarjeta de Credito'),
                ('3', 'Prestamo'), ('5', 'Cheque'),('6', 'Cuenta Contable'),('7', 'Tarjeta Debito Popular'),
        
        ), default='1', string='Tipo de Cuenta'),
    }

res_partner_bank_ext()
