# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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



import base64
import logging
import simplejson

import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, Home
logger = logging.getLogger(__name__)


class Uplodear(Home):
    @http.route('/web/binary/upload_multi_attachment', type='http', auth="user")
    @serialize_exception
    def upload_attachment(self, callback, model, id, ufile):
        files = http.request.httprequest.files.getlist('ufile')
        Model = request.session.model('ir.attachment')
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        try:
            args = {}
            for ufile in files:
                attachment_id = Model.create({
                    'name': ufile.filename,
                    'datas': base64.encodestring(ufile.read()),
                    'datas_fname': ufile.filename,
                    'res_model': model,
                    'res_id': int(id)
                }, request.context)
                args[attachment_id] = ufile.filename
        except Exception:
            args = {'error': "Something horrible happened"}
            logger.exception("Fail to upload attachment %s" % ufile.filename)
        return out % (simplejson.dumps(callback), simplejson.dumps(args))
