#!/usr/bin/python

import xmlrpclib

# Adapt these values to your setup.
HOST='erp.goweb.com.do' # the IP address where the server is running
PORT=8069
DB='gowebdb'
USER='admin'
PASS='4Mzuy2tGJXMCk1'

url = 'http://%s:%d/xmlrpc/' % (HOST,PORT)
common_proxy = xmlrpclib.ServerProxy(url+'common')
object_proxy = xmlrpclib.ServerProxy(url+'object')

# Simple wrapper function that provides the dbname, user id,
# and password for us. This uses the uid returned at step 1.
def execute(*args):
    return object_proxy.execute(DB,uid,PASS,*args)

# 1. Login so we have the user id for next requests.
uid = common_proxy.login(DB,USER,PASS)
print "Logged in as %s (uid:%d)" % (USER,uid)

# Search Products, strip internal reference and update it back
products = execute('product.product','search',[])
product_data = execute('product.product','read',products, ['default_code'])
for product in product_data:
    if product['default_code']:
	code = product['default_code'].strip()
	if len(code) != len(product['default_code']):
	    print "Found internal reference [%s] with spaces and is cleaned now !"%(code)
    	execute('product.product','write', product['id'], {'default_code':code})




	

