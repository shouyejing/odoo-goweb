# -*- coding: utf-8 -*-
{
    'name': 'Inter Company Move',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'summary': 'Moves documents around companies in a multicompany environment,',
    'description': """
Inter Company Move
==================
    """,
    'author':  'ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'sale',#we add sale depency because invoice report inheritance error, it also make sense because this module is only usefull if sale is installed
        'l10n_ar_invoice_sale', #we add this dependency also for same error mentioned above
    ],
    'data': [
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
        'wizard/inter_company_move_wizard_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: