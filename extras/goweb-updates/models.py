# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, expression, orm
from openerp import models, api
import pdb

class purchase_order(orm.Model):

    _inherit = 'purchase.order'
    _columns = {
        'order_id': fields.many2one('sale.order', 'Sale Order', readonly=True)
    }
purchase_order()


class procurement_order(osv.Model):
    _inherit = 'procurement.order'

    def make_po(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        res=super(procurement_order,self).make_po(cr, uid, ids, context=context)
        for proc,lines in res.iteritems():
            proc_rec = self.browse(cr, uid, proc, context)
            sale_order = self.pool.get('sale.order').search(cr, uid, [('name', 'ilike', proc_rec.purchase_id.origin)])
            #purchase_order = self.pool.get('purchase.order').search
            self.pool.get('purchase.order').write(cr, uid, proc_rec.purchase_id.id,
                                            {'order_id':sale_order and sale_order[0] or False})
        return res


class gowebupdates(osv.osv):

    _inherit = 'account.move'

    _columns = {
        'state': fields.selection(
              [('draft','Unposted'),
               ('reviewed', 'Reviewed'),
               ('posted','Posted')], 'Status',
              required=True, readonly=True, copy=False,
              help='All manually created new journal entries are usually in the status \'Unposted\', '
                   'but you can set the option to skip that status on the related journal. '
                   'In that case, they will behave as journal entries automatically created by the '
                   'system on document validation (invoices, bank statements...) and will be created '
                   'in \'Posted\' status.'),
    }

    def button_reviewed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'reviewed'})
        return False

class saleorderdone(osv.osv):
     
    _inherit = 'sale.order'

    def button_set_to_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})

    def button_set_to_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
