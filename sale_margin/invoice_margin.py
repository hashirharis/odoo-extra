##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields,osv
import pooler
from tools import config
import time

class account_invoice_line(osv.osv):
	_name = "account.invoice.line"
	_inherit = "account.invoice.line"
	_columns = {
		'cost_price': fields.float('Cost Price', digits=(16, 2)),
	}
	def write(self, cr, uid, ids, vals, context={}):
		if vals.get('product_id' , False):
			res=self.pool.get('product.product').read(cr, uid, [vals['product_id']], ['standard_price'])
			vals['cost_price']=res[0]['standard_price']
		return super(account_invoice_line, self).write(cr, uid, ids, vals, context)

	def create(self, cr, uid, vals, context={}):
		if vals.get('product_id',False):
			res=self.pool.get('product.product').read(cr, uid, [vals['product_id']], ['standard_price'])
			vals['cost_price']=res[0]['standard_price']
		return super(account_invoice_line, self).create(cr, uid, vals, context)
account_invoice_line()


