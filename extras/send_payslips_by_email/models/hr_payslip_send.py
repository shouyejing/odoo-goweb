# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
#This software and associated files (the "Software") may only be used (executed,
#modified, executed after modifications) if you have purchased a valid license
#from the authors, typically via Odoo Apps, or if you have received a written
#agreement from the authors of the Software (see the COPYRIGHT section below).
#
#You may develop Odoo modules that use the Software as a library (typically
#by depending on it, importing it and using its resources), but without copying
#any source code or material from the Software. You may distribute those
#modules under the license of your choice, provided that this license is
#compatible with the terms of the Odoo Proprietary License (For example:
#LGPL, MIT, or proprietary licenses similar to this one).
#
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#or modified copies of the Software.
#
#The above copyright notice and this permission notice must be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2016 Bernard K Too<bernard.too@optima.co.ke>

from openerp import models, fields, api, _

class SendMultiPayslips(models.TransientModel):
    _name='hr.payslip.send'

    @api.multi
    def multi_send_by_email(self):
        for slip in self.env[self._context.get('active_model')].browse(self._context.get('active_ids')):
            composer_values = {}
            ctx = {}
            ctx.update(self._context)
            ctx.update(slip.SendByEmail().get('context'))
            template_values = [
                ctx.get('default_template_id'),
                ctx.get('default_composition_mode'),
                ctx.get('default_model'),
                ctx.get('default_res_id'),
            ]
            composer_values.update(self.env['mail.compose.message'].onchange_template_id(*template_values).get('value', {}))
            composer_values['attachment_ids'] = [(6, 0, composer_values.get('attachment_ids', None))]
            composer_values['partner_ids'] = [(6, 0, composer_values.get('partner_ids', None))]
            self.env['mail.compose.message'].with_context(ctx).create(composer_values).with_context(ctx).send_mail()





