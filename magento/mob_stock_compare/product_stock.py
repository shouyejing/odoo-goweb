# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

import xmlrpclib
from openerp import api, fields, models, _
from openerp.addons.magento_bridge.mob import XMLRPC_API
from openerp.exceptions import ValidationError
from openerp.tools import float_compare

import logging
_logger = logging.getLogger(__name__)

################## ..........Magento Product inheritance .........########


class product_stock(models.Model):
    _inherit = "magento.product"

    @api.multi
    def _get_product_stock_compare(self):
        ctx = dict(self._context or {})
        map_objs = ''
        if ctx.get('do_all'):
            map_objs = self.search([('pro_name', '!=', False)])
        else:
            start = ctx.get('start')
            end = ctx.get('end')
            map_objs = self.search(
                [('pro_name', '!=', False), ('id', '>=', start), ('id', '<=', end)])
        prod_stock = self._get_magento_stock_price(
            map_objs.mapped('mag_product_id'), 'stock')
        tree_id = self.env.ref(
            'mob_stock_compare.mob_product_stock_tree', False)
        count = len(map_objs)
        for obj in map_objs:
            if obj.pro_name.type == 'service' and obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                obj.stock_error = False
                continue
            count = count - 1
            oe_qty_available = obj.pro_name.qty_available
            mage_id = str(obj.mag_product_id)
            _logger.info(
                "-------(QOH)-----counter => %r : magentoId => %r", count, mage_id)
            mag_qty_available = prod_stock.get(mage_id)
            if not mag_qty_available:
                mag_qty_available = "Product doesn't exist at Magento"
                stock_error = True
            else:
                stock_error = self._get_report(
                    oe_qty_available, mag_qty_available)
            mag_qty_available = str(mag_qty_available)
            obj.write({
                'mag_qty_available': mag_qty_available,
                'oe_qty_available': oe_qty_available,
                'stock_error': stock_error
            })
            # if sleep == 500:
            #     _logger.info("-----Sleep-----For 3 seconds------")
            #     time.sleep(3)
            #     self._cr.commit()
            #     sleep = 0

        return {
            'name': 'Stock Comparison',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,from',
            'res_model': 'magento.product',
            'views': [(tree_id.id, 'tree')],
            'view_id': tree_id.id,
            'target': 'current',
            'domain': [('stock_error', '=', True)]
        }

    @api.model
    def _get_report(self, oe_qty_available, mag_qty_available):
        stock_error = False
        if float_compare(oe_qty_available, float(mag_qty_available), precision_digits=2):
            stock_error = True
        return stock_error

    @api.multi
    def _get_product_price_compare(self):
        ctx = dict(self._context) or {}
        map_objs = ''
        if ctx.get('do_all'):
            map_objs = self.search([('pro_name', '!=', False)])
        else:
            start = ctx.get('start')
            end = ctx.get('end')
            map_objs = self.search(
                [('pro_name', '!=', False), ('id', '>=', start), ('id', '<=', end)])
        prod_price = self._get_magento_stock_price(
            map_objs.mapped('mag_product_id'), 'price')
        tree_id = self.env.ref(
            'mob_stock_compare.mob_product_price_tree', False)
        count = len(map_objs)
        for obj in map_objs:
            if obj.pro_name.type == 'service' and obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                obj.stock_error = False
                continue
            count = count - 1
            mage_id = str(obj.mag_product_id)
            oe_price = obj.pro_name.list_price
            _logger.info("---price_compare---counter => : %r : %r",
                         count, obj.oe_price)
            mag_price = prod_price.get(mage_id)
            if not mag_price:
                mag_price = "Product doesn't exist at Magento"
                price_error = True
            else:
                price_error = self._get_price_report(oe_price, mag_price)
            mag_price = str(mag_price)
            obj.write({
                'oe_price': oe_price,
                'mag_price': mag_price,
                'price_error': price_error
            })

        return {
            'name': 'Price Comparison',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,from',
            'res_model': 'magento.product',
            'views': [(tree_id.id, 'tree')],
            'view_id': tree_id.id,
            'target': 'current',
            'domain': [('price_error', '=', True)]
        }

    def _get_magento_stock_price(self, mag_prod_list, oe_from):
        _logger.info('--oe_from--------%r', oe_from)
        connection = self.env['magento.configure']._create_connection()
        if connection:
            url = connection[0]
            session = connection[1]
            server = xmlrpclib.Server(url)
            try:
                mage_price = server.call(session, 'magerpsync.product_price', [
                                         mag_prod_list, oe_from])
                if mage_price:
                    return mage_price
            except xmlrpclib.Fault, e:
                return [0, '\nError in fetching price due to %s' % (str(e))]
        return False

    @api.model
    def _get_price_report(self, oe_price, mag_price):
        price_error = False
        _logger.info("-------------oe_price : %r : mag_price : %r",
                     oe_price, mag_price)
        if float_compare(oe_price, float(mag_price), precision_digits=2):
            price_error = True
        return price_error

    oe_qty_available = fields.Float(string='Odoo (Quantity On Hand)')
    mag_qty_available = fields.Char(string='Magento (Quantity On Hand)')
    stock_error = fields.Boolean(string='Stock Mis-match')

    oe_price = fields.Float(string='Odoo (Price)')
    mag_price = fields.Char(string='Magento (Price)')
    price_error = fields.Boolean(string='Price Mis-match')

    @api.model
    def start_bulk_product_stock_sync(self):
        ctx = dict(self._context or {})
        if ctx.has_key('active_ids'):
            objs = self.env['magento.configure'].with_context(
                ctx).search([('active', '=', True)])
            for obj in objs:
                url = obj.name + XMLRPC_API
                user = obj.user
                pwd = obj.pwd
                try:
                    server = xmlrpclib.Server(url)
                    session = server.login(user, pwd)
                except xmlrpclib.Fault, e:
                    text = 'Error, %s Magento details are Invalid.' % e
                except IOError, e:
                    text = 'Error, %s.' % e
                except Exception, e:
                    text = 'Error in Magento Connection.'

                for map_id in ctx['active_ids']:
                    if not session:
                        return [0, text]
                    else:
                        try:
                            stock = 0
                            map_obj = self.browse(map_id)
                            if map_obj.pro_name.type == 'service' and map_obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                                continue
                            if map_obj.mag_qty_available == "Product doesn't exist at Magento":
                                continue
                            if map_obj.oe_qty_available > 0:
                                stock = 1
                            update_data = [map_obj.mag_product_id, {
                                'manage_stock': 1, 'qty': map_obj.oe_qty_available, 'is_in_stock': stock}]
                            stock_search = server.call(
                                session, 'product_stock.update', update_data)
                            if stock_search:
                                map_obj.stock_error = False
                        except Exception, e:
                            return [0, ' Unable to search stock for product id %s' % map_obj.mag_product_id]
            partial = self.env['message.wizard'].with_context(
                ctx).create({'text': 'Stock Updated At Magento'})

            return {'name': ("Information"),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'message.wizard',
                    'view_id': self.env.ref('magento_bridge.message_wizard_form1').id,
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    }

    @api.model
    def start_bulk_product_price_sync(self):
        ctx = dict(self._context or {})
        if ctx.has_key('active_ids'):
            objs = self.env['magento.configure'].with_context(
                ctx).search([('active', '=', True)])
            for obj in objs:
                url = obj.name + XMLRPC_API
                user = obj.user
                pwd = obj.pwd
                try:
                    server = xmlrpclib.Server(url)
                    session = server.login(user, pwd)
                except xmlrpclib.Fault, e:
                    text = 'Error, %s Magento details are Invalid.' % e
                except IOError, e:
                    text = 'Error, %s.' % e
                except Exception, e:
                    text = 'Error in Magento Connection.'

                for map_id in ctx['active_ids']:
                    if not session:
                        return [0, text]
                    else:
                        try:
                            stock = 0
                            map_obj = self.browse(map_id)
                            if map_obj.pro_name.type == 'service' and map_obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                                continue
                            if map_obj.mag_price == "Product doesn't exist at Magento":
                                continue
                            if map_obj.oe_price > 0:
                                stock = 1
                            update_data = [map_obj.mag_product_id, {
                                'price': map_obj.oe_price}]
                            stock_search = server.call(
                                session, 'catalog_product.update', update_data)
                        except Exception, e:
                            return [0, ' Unable to search price for product id %s' % map_obj.mag_product_id]
            partial = self.env['message.wizard'].with_context(
                ctx).create({'text': 'Price Updated At Magento'})
            return {'name': ("Information"),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'message.wizard',
                    'view_id': self.env.ref('magento_bridge.message_wizard_form1').id,
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    }

    @api.model
    def mob_stock_sync_cron(self):
        ctx = dict(self._context) or {}
        instance_ids = self.env['magento.configure'].with_context(
            ctx).search([('active', '=', True)])
        for instance_obj in instance_ids:
            mapping_objs = self.env['magento.product'].with_context(
                ctx).search([('instance_id', '=', instance_obj.id)])
            if mapping_objs:
                mapping_objs._get_product_stock_compare()
                for mapping_obj in mapping_objs:
                    if mapping_obj.pro_name.type == 'service' and mapping_obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                        continue
                    if mapping_obj.stock_error:
                        mapping_obj._get_mage_product_stock_cron()
        return True

    @api.one
    def _get_mage_product_stock_cron(self):
        ctx = dict(self._context) or {}
        connection = self.env['magento.configure'].with_context(
            ctx)._create_connection()
        if connection:
            url = connection[0]
            session = connection[1]
            server = xmlrpclib.Server(url)
            if self.mag_qty_available == "Product doesn't exist at Magento":
                return True
            try:
                mage_product_id = self.mag_product_id
                quantity = self.oe_qty_available
                stock = 0
                if quantity > 0:
                    stock = 1
                update_data = [mage_product_id, {
                    'manage_stock': 1, 'qty': quantity, 'is_in_stock': stock}]
                _logger.info(
                    "-----------1------------update_data----------Template Attribute: %r", update_data)
                output = server.call(
                    session, 'product_stock.update', update_data)
                _logger.info(
                    "-----------2------------output----------Template Attribute: %r", output)
            except Exception, e:
                pass
        return True

    @api.model
    def mob_price_sync_cron(self):
        ctx = dict(self._context) or {}
        instance_ids = self.env['magento.configure'].with_context(
            ctx).search([('active', '=', True)])
        for instance_obj in instance_ids:
            mapping_objs = self.env['magento.product'].with_context(
                ctx).search([('instance_id', '=', instance_obj.id)])
            if mapping_objs:
                mapping_objs._get_product_price_compare()
                for mapping_obj in mapping_objs:
                    if mapping_obj.pro_name.type == 'service' and mapping_obj.pro_name.preferred_supplier == "PUNTOMAC S R L":
                        continue
                    if mapping_obj.price_error:
                        mapping_obj._get_mage_product_price_cron()
        return True

    @api.one
    def _get_mage_product_price_cron(self):
        ctx = dict(self._context) or {}
        connection = self.env['magento.configure'].with_context(
            ctx)._create_connection()
        if connection:
            url = connection[0]
            session = connection[1]
            server = xmlrpclib.Server(url)
            if self.mag_price == "Product doesn't exist at Magento":
                return True
            try:
                mage_product_id = self.mag_product_id
                price = self.oe_price
                update_data = [mage_product_id, {'price': price}]
                _logger.info(
                    "-----------1------------update_data----------Template Attribute: %r", update_data)
                output = server.call(
                    session, 'catalog_product.update', update_data)
                _logger.info(
                    "-----------2------------output----------Template Attribute: %r", output)
            except Exception, e:
                pass
        return True
