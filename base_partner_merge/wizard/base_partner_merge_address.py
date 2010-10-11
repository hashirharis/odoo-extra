# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
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

from osv import fields, osv
from tools.translate import _


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        if context is None:
            context = {}
        if context.get('merge', False):
            partner_address_obj = self.pool.get('res.partner.address')
            add2 = partner_address_obj.browse(cr, uid, context['merge'], context=context).partner_id.id
            args.append(('partner_id', '=', add2))
        return super(res_partner_address, self).search(cr, uid, args, offset, limit, 
                order, context=context, count=count)
res_partner_address()


class base_partner_merge_address(osv.osv_memory):
    '''
    Merges two Addresses
    '''
    _name = 'base.partner.merge.address'
    _description = 'Merges two partners'

    _columns = {
        'address_id1':fields.many2one('res.partner.address', 'Address1', required=True), 
        'address_id2':fields.many2one('res.partner.address', 'Address2', required=True), 
    }

    def action_next(self, cr, uid, ids, context=None):
        
        value = {
            'name': _('Select Values'), 
            'view_type': 'form', 
            'view_mode': 'form', 
            'res_model': 'base.partner.merge.address.values', 
            'view_id': False, 
            'target': 'new', 
            'type': 'ir.actions.act_window', 
        }
        return value
base_partner_merge_address()


class base_partner_merge_address_values(osv.osv_memory):
    '''
    Merges two partners
    '''
    _name = 'base.partner.merge.address.values'
    _description = 'Merges two Addresses'

    _columns = {
        'name':fields.char('Name', size=64), 
    }

    _values = {}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(base_partner_merge_address_values, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        cr.execute("SELECT id, name, field_description, ttype, required, relation from ir_model_fields where model='res.partner.address'")
        field_datas = cr.fetchall()
        
        #get address data
        merge_obj = self.pool.get('base.partner.merge.address')
        add_ids = merge_obj.search(cr, uid, [], context=context)
        if not add_ids:
            return res
        add_data = merge_obj.browse(cr, uid, add_ids[-1], context=context)
        if add_data.address_id1 == add_data.address_id2:
            raise osv.except_osv(_("Warning!"), _("There is no difference in selected addresses."))
        myxml, merge_fields, self._values, columns = self.pool.get('base.partner.merge')._build_form(cr, uid, field_datas, add_data.address_id1, add_data.address_id2)
        self._columns.update(columns)
        res['arch'] = myxml
        res['fields'] = merge_fields
        return res

    def action_merge(self, cr, uid, ids, context=None):
        pool = self.pool
        address_obj = pool.get('res.partner.address')
        merge_obj = self.pool.get('base.partner.merge.address')
        add_ids = merge_obj.search(cr, uid, [], context=context)
        if not add_ids:
            return {}
        add_data = merge_obj.browse(cr, uid, add_ids[-1], context=context)
        add1 = add_data.address_id1.id
        add2 = add_data.address_id2.id

        res = self.read(cr, uid, ids, context=context)[0]
        res.update(self._values)

        if hasattr(address_obj, '_sql_constraints'):
            #for uniqueness constraint (vat number for example)...
            c_names = []
            remove_field = {}
            for const in address_obj._sql_constraints:
                c_names.append('res_partner_address_' + const[0])
            if c_names:
                c_names = tuple(map(lambda x: "'"+ x +"'", c_names))
                cr.execute("""select column_name from \
                            information_schema.constraint_column_usage u \
                            join  pg_constraint p on (p.conname=u.constraint_name) \
                            where u.constraint_name in (%s) and p.contype='u' """ % c_names)
                for i in cr.fetchall():
                    remove_field[i[0]] = None

        remove_field.update({'active': False})
        address_obj.write(cr, uid, [add1, add2], remove_field, context=context)
        add_id = address_obj.create(cr, uid, res, context=context)

        # For one2many fields on res.partner.address
        cr.execute("select name, model from ir_model_fields where relation='res.partner.address' and ttype not in ('many2many', 'one2many');")
        for name, model_raw in cr.fetchall():
            if hasattr(pool.get(model_raw), '_auto'):
                if not pool.get(model_raw)._auto:
                    continue
            elif hasattr(pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(pool.get(model_raw), '_columns'):
                    from osv import fields
                    if pool.get(model_raw)._columns.get(name, False) and isinstance(pool.get(model_raw)._columns[name], fields.many2one):
                        model = model_raw.replace('.', '_')
                        cr.execute("update "+model+" set "+name+"="+str(add_id)+" where "+str(name)+" in ("+str(add1)+", "+str(add2)+")")
        return {}

base_partner_merge_address_values()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
