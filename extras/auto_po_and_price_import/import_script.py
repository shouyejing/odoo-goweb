# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd
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
import os
import csv
import math
import logging
import glob
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp import tools
_logger = logging.getLogger(__name__)


class sync_back2_magento(models.Model):
    _name = 'sync.back2.magento'
     
    @api.model
    def sync_products_back2_magento(self):
        email_template = self.env.ref('auto_po_and_price_import.email_template_cron2', False)
        status = ''
        status_log = ''
        try:
            _logger.info('''Started synchronizing products back to Magento as pricelist import just finished !''')
            ctx = self._context.copy()
            self.pool.get('magento.synchronization').update_products_via_cron(self._cr, self._uid, context=ctx)
            _logger.info(''' Successfully !''')
            status = 'Successful !'
        except Exception, e:
            _logger.info('Encountered problems while synchronizing products to Magento %s!'%(e))
            status_log = ' and had these error %s !'%(e)
            status = 'Unsuccessful !'
        email_template.with_context(status=status,status_log=status_log).send_mail(None,force_send=True)
        return True
    
class import_supplier_pricelist(models.Model):
    _name = 'import.supplier.pricelist'
    
    @api.model
    def import_supplier_price(self):
        pricelist_url = self.env['ir.config_parameter'].get_param('pricelist_url')
        if not pricelist_url:
            _logger.warning('Please add pricelist_url to System Parameters')
        else:
            #try:    
            self.run_script(pricelist_url)
         #   except Exception,e:
          #      _logger.error('An Error occured while importing pricelist (%s)',e)
        return True
    
    @api.model
    def get_parent_location(self, supplier):
        warehouse = self.env['stock.warehouse'].search([('name','=',supplier)])
        if warehouse:
            return warehouse.view_location_id
        return []
        
    @api.model
    def run_script(self, pricelist_url):
        email_template = self.env.ref('auto_po_and_price_import.email_template_log', False)
        product_list = {}
        supplier_stock_update = {}
        found = False
        for supplier_dir in os.listdir(pricelist_url):
            logfile = ''
            supplier = self.env['res.partner'].search([('name','ilike',supplier_dir),('supplier','=',True)])
            warnings = 0
            sup_dir = str(pricelist_url) + str(supplier_dir)
            files_to_imp = glob.glob(sup_dir + "/*.csv") + glob.glob(sup_dir + "/*.txt") + glob.glob(sup_dir + "/*.TXT")
            parent_location_id = self.get_parent_location(supplier_dir)
            product_list.update({supplier_dir:[]})
            for imp_file in files_to_imp:
                file_string = imp_file.split('/')
                if file_string and file_string[-1] and 'Processed_' in file_string[-1]:
                    pass
                else:
                    _logger.info('''Start Processing csv from : %s''',imp_file)
                    logfile += str('\nINFO:Start Processing csv from : %s'%imp_file)
                    reader = csv.reader(open(imp_file,'rb'))
                    i = 1
                    for row in reader:
                        if len(row) < 7 or len(row) > 8:
                            continue
                        #Comment/Remove it if your CSV has no header row.
                        if i == 1:
                            i = i + 1
                            continue
                        if row[3]:
                            model_code = row[3].strip()
                            model_code = model_code.replace(" ","")
                        elif row[1].find('M/') > 0:
                            model_code = row[1].split('M/')[1]
                            model_code = model_code.replace(" ","")
                        else:
                            _logger.warning('''No Model info found in CSV row %s ! SKipping Import ! ''',row)
                            logfile += str('\nWarning:No Model info found in CSV row %s ! SKipping Import ! '%row)
                            warnings += 1
                            continue
                        product = self.env['product.product'].search([('default_code','=',model_code)])
                        if len(product) > 1:
                            _logger.warning('''More then 1 product with Internal reference (%s) found in the database ! SKipping Import ! ''',model_code)
                            logfile += str('\nWarning:More then 1 product with Internal reference (%s) found in the database ! SKipping Import ! '%model_code)
                            warnings += 1
                            continue
                        if product:
                            product_list[supplier_dir].append(product)
                            found = True
                        else:
                            _logger.warning('''Product [%s] %s not found in the database ! SKipping Import ! '''%(model_code,tools.ustr(row[1])))
                            logfile += str('\nWarning:Product ([%s] %s) not found in the database ! SKipping Import ! '%(model_code, row[1]))
                            warnings += 1
                            continue
                            
                        if supplier and product:
                            supplierinfo_id = self.env['product.supplierinfo'].search([('name','=',supplier.id), 
                                ('product_tmpl_id','in',[product.product_tmpl_id.id])])
                               
                            if not supplierinfo_id:
                                _logger.warning('''Supplier (%s) on product %s not found in the database ! Creating a new one ! '''%(supplier.name,model_code))
                                logfile += str('\nWarning:Supplier (%s) on product %s not found in the database ! Creating a new one ! '%(supplier.name,model_code))
                                warnings += 1
                                supplierinfo_vals = {
                                    'name': supplier.id,
                                    'pricelist_ids': [(0, 0, {'min_quantity': 0.0, 'price': row[5] and float(row[5].strip()) or 0.0,
                                                              'sale_price': row[4] and float(row[4].strip()) or 0.0})],
                                    'product_tmpl_id': product and product.product_tmpl_id.id,
                                }
                                self.env['product.supplierinfo'].create(supplierinfo_vals)
                            else:
                                pricelist_id = self.env['pricelist.partnerinfo'].search([('suppinfo_id','=',supplierinfo_id.id)])
                                if pricelist_id:
                                    pricelist_id.unlink()
                                supplierinfo_vals = {
                                    'pricelist_ids': [(0, 0, {'min_quantity': 0.0, 'price': row[5] and float(row[5].strip()) or 0.0,
                                                              'sale_price':row[4] and float(row[4].strip()) or 0.0})],
                                    }
                                supplierinfo_id.write(supplierinfo_vals)
                                    
                            if row[6] and parent_location_id:
                                stock_location_id = self.env['stock.location'].search([('id', 'child_of', [parent_location_id.id]),('usage','=' ,'supplier')])
                                if stock_location_id:
                                    if not stock_location_id in supplier_stock_update:
                                        supplier_stock_update.update({stock_location_id:{}})
                                    supplier_stock_update[stock_location_id].update({product:row[2].strip()})
                                else:
                                    _logger.info('Supplier stock location not found under %s ! Skipping the stock !'%(parent_location_id.name+'/'+row[6]))
                                    logfile += str('\nINFO:Supplier stock location not found under %s ! Skipping the stock !'%(parent_location_id.name+'/'+row[6]))
                    if len(supplier_stock_update):
                        _logger.info('Adding stock to location of suppliers ! ''')
                        logfile += str('\nAdding stock to location of suppliers ! ''')
                        self.adjust_inventory(supplier_stock_update)
                        logfile += str('\nFinish adding stock to location of suppliers ! ''')
                        _logger.info('Finish adding stock to location of suppliers ! ''')
                    os.rename(imp_file, sup_dir + "/Processed_" + file_string[-1])
                    state = 'done'
                    if warnings > 0:
                        state = 'with warnings'
                    _logger.info('''Finished processing csv : %s''',imp_file)
                    logfile += '\nINFO:Finished processing csv : %s'%imp_file
                    values = dict(
                        name='%s.txt'%(supplier_dir),
                        datas_fname='%s.txt'%(supplier_dir),
                        res_model='import.supplier.pricelist',
                        type='binary',
                        datas=logfile.encode('base64'),
                    )
                    attach_id = self.env['ir.attachment'].create(values)
                    email_template.write({'attachment_ids': [(6, 0, [attach_id.id])]})
                    email_template.with_context(supplier=supplier.name,status=state).send_mail(None,force_send=True)
                    attach_id.unlink()
        if not found:
            _logger.info('No Product / csv found to process..... !')
        else:
            logfile1 = ''
            logfile1 += '<br />Finished processing csv files now starting the calculation phase<br /> '
            magento_connection = self.env['magento.configure'].search([('active','=',True)])
            reset_stock = {}
            reset_stock[magento_connection.location_id] = {}
            for _, prod_list in product_list.iteritems():
                reset_stock[magento_connection.location_id].update({}.fromkeys(prod_list, 0.0))
            _logger.info('''Calculating the cheapest supplier !''')
            logfile1 += str('<br />Calculating the cheapest supplier !<br />')
            res_value = self.get_cheapest_supplier_or_value(product_list)
            stock_todo = {}
            for product, values in res_value.iteritems():
                #_logger.info('''Updating product info %s !'''%(tools.ustr(product.name)))
                #logfile1 += str('<br />Updating product info %s !<br />'''%(tools.ustr(product.name)))
                _logger.info('''Updating product info !''')
                logfile1 += str('<br />Updating product info !<br />''')
                preferred_supplier = values.get('preferred_supplier','')
                if not stock_todo.has_key(preferred_supplier):
                    stock_todo.update({preferred_supplier:{}})
                product.write({'lst_price': values.get('list_price',0.0),'standard_price':values.get('standard_price',0.0),
                               'preferred_supplier':preferred_supplier})
                if not stock_todo[preferred_supplier].has_key(product):
                    stock_todo[preferred_supplier].update({product:0.0})
                stock_todo[preferred_supplier].update({product:values.get('qty',0.0)})
            _logger.info('Resetting default warehouse location %s stock to 0 for all good products in CSV and DB !' %(magento_connection.location_id.name))
            logfile1 += str('<br />Resetting default warehouse location %s stock to 0 for all good products in CSV and DB !<br />' %(magento_connection.location_id.name))
            self.adjust_inventory(reset_stock, message='Reset')
            _logger.info('starting to move stock to default warehouse..... !')
            logfile1 += str('<br />starting to move stock to default warehouse..... !<br />')
            self.set_stock_default_warehouse(stock_todo)
            _logger.info('Processed.....finally !')
            logfile1 += str('<br />Processed.....finally ! <br />')
            mail_body = """
                    <div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
                        <p>%s</p>
                    </div>
                    """%(logfile1)
            mail_vals = {
                    'email_from': email_template.email_from,
                    'email_to': email_template.email_to,
                    'subject': 'CSV Import calculation phase !',
                    'body_html': mail_body,
                }
            mail = self.env['mail.mail'].create(mail_vals)
            mail.sudo().send()
        return True
    
    def adjust_inventory(self, product_data, message='INV'):
        for stock_location_id, prodinfo in product_data.iteritems():
            line_data = []
            _logger.info('''Adding stock to  %s location ! ''',stock_location_id.location_id.location_id.name +'/'+stock_location_id.location_id.name+'/'+stock_location_id.name)
            for prod, qty in prodinfo.iteritems():
                if message == 'Reset':
                    _logger.info('Reset stock to 0 qty for product %s at %s location !..... !'%(prod.name,stock_location_id.location_id.name+'/'+stock_location_id.name))
                else: 
                    _logger.info('Moving stock of %s qty of product %s to %s location !..... !'%(qty, prod.name,stock_location_id.location_id.name+'/'+stock_location_id.name))
                if float(qty) < 0.0:
                    _logger.info('Product %s has negative quantity (%s) in CSV. Making it to Zero !..... !'%(prod.name,qty))
                    qty = 0.0 
                line_data.append((0,0,{
                            'product_qty': float(qty),
                            'location_id': stock_location_id.id,
                            'product_id': prod.id,
                            'product_uom_id': prod.uom_id.id}))
            inventory_id = self.env['stock.inventory'].create(
                                    {'name': _('%s: All Products !') % (message),
                                    'location_id': stock_location_id.id,
                                    'filter': 'none',
                                    'line_ids':line_data
                                    })
            inventory_id.with_context(stock_from=False).action_done()
        return True
    
    def clean_inventory(self, locations):
        inventory = self.env['stock.inventory'].search(['|', ('location_id','in', locations),('name','ilike','Reset:%')])
        return inventory.unlink()
        
    def set_stock_default_warehouse(self, stock_todo={}, reverse=False):
        move_obj = self.env['stock.move']
        magento_connection = self.env['magento.configure'].search([('active','=',True)])
        default_stock_location = magento_connection.location_id
        location_to_clean = []
        for supplier, values in stock_todo.iteritems():
            parent = self.get_parent_location(supplier)
            if not len(parent):continue
            child_loc = self.env['stock.location'].search([('id', 'child_of', [parent.id]),('usage','=' ,'supplier')])
            location_to_clean.append(child_loc.id)
            location_id = child_loc.id
            location_dest_id = default_stock_location.id
            if reverse:
                location_id = default_stock_location.id
                location_dest_id = child_loc.id
            for product, qty in values.iteritems():
                _logger.info('Moving stock of %s qty of product %s to default warehouse location %s !..... !'%(qty, product.name,default_stock_location.name))
                move = move_obj.create({'name':'Internal Transfers',
                                       'product_id':product.id,
                                       'product_uom_qty':qty,
                                       'location_id':location_id,
                                       'location_dest_id':location_dest_id,
                                       'product_uom':product.uom_id.id})
                move.with_context(stock_from=False).action_done()
        _logger.info('Stock Moved Successfully !')
        _logger.info('Cleaning Inventory Adjustment Entries !')
        self.clean_inventory(location_to_clean)
        _logger.info('finished Cleaning Inventory Adjustment Entries !')
        return True

    def get_cheapest_supplier_or_value(self, product_list, return_value=True):   
        cost_price = {}
        res_digits = self.env['decimal.precision'].sudo().precision_get('Product Price')
        round_digits = res_digits or 2
        for useless, product1 in product_list.iteritems():
            for product in product1:
                if not cost_price.has_key(product):
                    cost_price.update({product:{}})    
                for supplierinfo_id in product.seller_ids:
                    if not cost_price[product].has_key(supplierinfo_id.name):
                        cost_price[product].update({supplierinfo_id.name:{}})
                    qty = 0.0
                    parent_location_id = self.get_parent_location(supplierinfo_id.name.name)
                    if parent_location_id:
                        quants = self.env['stock.quant'].search([('location_id', 'child_of', parent_location_id.id),('product_id','=',product.id)])
                        for quant in quants:
                            qty += quant.qty
                        pricelist_id = supplierinfo_id.name.property_product_pricelist_purchase
                        sale_pricelist = supplierinfo_id.name.property_product_pricelist
                        if qty >= supplierinfo_id.name.stock_limit_per_supplier or qty == 0.0:
                            sale_price = 0.0
                            purchase_price = 0.0
                            final_sprice = 0.0
                            rounded_saleprice_new = 0.0
                            if pricelist_id: 
                                purchase_price = pricelist_id.price_get(product.id, 1.0, supplierinfo_id.name.id or False)[pricelist_id.id]
                            if sale_pricelist:
                                sale_price = sale_pricelist.price_get(product.id, 1.0, supplierinfo_id.name.id or False)[sale_pricelist.id]
                                if sale_price > 0.0:
                                    final_sprice = product.taxes_id.compute_all(sale_price, 1, product=product)
                                    tax_percent = (round((((final_sprice['total_included'] - final_sprice['total']) / final_sprice['total'])*100),round_digits) + 100)/100
                                    rounded_saleprice = math.ceil(final_sprice['total_included'] / 100.0)*100 - 0.01
                                    rounded_saleprice_new = round(rounded_saleprice / tax_percent,round_digits)
                            cost_price[product][supplierinfo_id.name] = {'sale_price':rounded_saleprice_new,'cost_price':purchase_price,'qty':qty}
        res_value = {}
        for prod, info in cost_price.iteritems():
            cheapest = 10000000
            sale_price = 0.0
            qty = 0.0
            supplier = False
            for supp, vals in info.iteritems():
                if vals.has_key('cost_price') and vals['cost_price'] < cheapest:
                    if prod:
                        if len(info.keys()) > 1 and vals['qty'] == 0.0:
                            continue
                        res_value.update({prod:{}})
                        res_value[prod].update(preferred_supplier=supp.name,standard_price=vals['cost_price'],list_price=vals['sale_price'],qty=vals['qty'])
                        cheapest = vals['cost_price']
                        supplier = supp
        if return_value:
            return res_value
        return supplier


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
