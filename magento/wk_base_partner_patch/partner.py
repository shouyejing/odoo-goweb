 # -*- coding: utf-8 -*-
##############################################################################
#		
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 webkul
#	 Author :
#				www.webkul.com	
#
##############################################################################

from openerp.osv import osv,fields


class res_partner(osv.osv):
	_inherit = 'res.partner'

	# def _handle_first_contact_creation(self, cr, uid, partner, context=None):
	# 	""" On creation of first contact for a company (or root) that has no address, assume contact address
	# 	was meant to be company address """
	# 	parent = partner.parent_id
	# 	address_fields = self._address_fields(cr, uid, context=context)
	# 	if parent and (parent.is_company or not parent.parent_id) and len(parent.child_ids) == 1 and \
	# 		any(partner[f] for f in address_fields) and not any(parent[f] for f in address_fields):
	# 		addr_vals = self._update_fields_values(cr, uid, partner, address_fields, context=context)
	# 		parent.update_address(addr_vals)
	# 		### Don't add is_company automatically ###
	# 		# if not parent.is_company:
	# 		# 	parent.write({'is_company': True})

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.name
			company = record.wk_company
			if company:
				name = company + ',' + name
			if record.parent_id and not record.is_company and record.parent_id.is_company and not company:
				name =  "%s, %s" % (record.parent_id.name, name)
			if context.get('show_address'):
				name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
				name = name.replace('\n\n','\n')
				name = name.replace('\n\n','\n')
			if context.get('show_email') and record.email:
				name = "%s <%s>" % (name, record.email)
			res.append((record.id, name))
		return res
		
	_columns = {
		'wk_address': fields.boolean('Address'),
		'wk_company': fields.char('Company', size=128),
	}