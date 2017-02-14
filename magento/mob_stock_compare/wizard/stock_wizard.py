# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

class ProductStockWizard(models.TransientModel):
	_name = "product.stock.wizard"

	options = fields.Selection([('all', 'All'), ('custom', 'Custom')], string="Choose the option", required=True)
	range_from = fields.Integer(string="From")
	range_to = fields.Integer(string="To")
	stock_price_info = fields.Char(string="Information", readonly=True)

	@api.one
	@api.onchange('options')
	def _compute_min_max(self):
		map_objs = self.env['magento.product'].search([('pro_name','!=',False)])
		min_id = min(map_objs.ids)
		max_id = max(map_objs.ids)
		self.stock_price_info = 'Enter the range of mapping ids between from %s to %s to comapre the Stock/Price' % (min_id, max_id)
	
	@api.constrains('range_from', 'range_to')
	def check_range(self):
		if not isinstance(self.range_from, int) or not isinstance(self.range_to, int):
				raise ValidationError("Range values should be Integer!")
		if self.range_from and self.range_to:
			if self.range_from >= self.range_to:
				raise ValidationError("Starting range should be lesser than Ending range!")
			elif self.range_from < 1:
				raise ValidationError("Starting range should be positive")

	@api.multi
	def stock_comapre(self):
		ctx = dict(self._context or {})
		if self.options == 'custom':
			ctx.update(
				start = self.range_from,
				end = self.range_to
				)
		if self.options == 'all':
			ctx.update(
				do_all ='yes'
				)
		return self.env['magento.product'].with_context(ctx)._get_product_stock_compare()

	@api.multi
	def price_comapre(self):
		ctx = dict(self._context or {})
		if self.options == 'custom':
			ctx.update(
				start = self.range_from,
				end = self.range_to
				)
		if self.options == 'all':
			ctx.update(
				do_all ='yes'
				)
		return self.env['magento.product'].with_context(ctx)._get_product_price_compare()
	
