# -*- coding: utf-8 -*-
from datetime import datetime
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class CheckMoves(models.Model):
    #_name = 'new_module.new_module'
    _inherit = 'stock.quant'

    def _check_last_move_date(self):
        move_obj = self.env['stock.move']
        magento_connection = self.env['magento.configure'].search([('active','=',True)])
        default_stock_location = magento_connection.location_id
        inv_lost_location = self.env['stock.location'].search([('usage', '=', 'inventory')])

        today = datetime.datetime.now()
        product_obj_ids = self.env['product.product'].search([('preferred_supplier', '!=', 'PUNTOMAC S R L')])

        for item in product_obj_ids:
            stock_quant_ids = self.env['stock.quant'].search([('product_id', '=', item.id),
                                                              ('location_id', '=', default_stock_location.id),
                                                              ('qty', '>', 0)])
            if stock_quant_ids:
                #import pdb; pdb.set_trace()
                stock_quant_id = stock_quant_ids[0]
                date_last_move = datetime.datetime.strptime(stock_quant_id.in_date, DEFAULT_SERVER_DATETIME_FORMAT)
                diff = today - date_last_move
                diff_days = diff.days
                if diff_days > 7:
                    #import pdb; pdb.set_trace()
                    str_diff_days = str(diff_days)
                    _logger.info('El producto |%s| - |%s| con el Suplidor Preferido |%s| tiene |%s| dias '
                                 'sin movimientos de entrada en el sistema' %(stock_quant_id.product_id.default_code,
                                                                              stock_quant_id.product_id.name,
                                                                              stock_quant_id.product_id.preferred_supplier,
                                                                              diff_days))
