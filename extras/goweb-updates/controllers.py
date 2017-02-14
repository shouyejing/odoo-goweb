# -*- coding: utf-8 -*-
from openerp import http

# class Goweb-updates(http.Controller):
#     @http.route('/goweb-updates/goweb-updates/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/goweb-updates/goweb-updates/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('goweb-updates.listing', {
#             'root': '/goweb-updates/goweb-updates',
#             'objects': http.request.env['goweb-updates.goweb-updates'].search([]),
#         })

#     @http.route('/goweb-updates/goweb-updates/objects/<model("goweb-updates.goweb-updates"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('goweb-updates.object', {
#             'object': obj
#         })