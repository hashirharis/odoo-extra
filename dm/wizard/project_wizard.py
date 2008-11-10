# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import wizard
import pooler
import netsvc

parameter_form = '''<?xml version="1.0"?>
<form string="Campaign Group" colspan="4">
    <field name="project_id" domain="[('parent_id','ilike','Direct Marketing Retro-Planning')]"
/>
</form>'''

parameter_fields = {
    'project_id': {'string':'Project', 'type':'many2one', 'required':True, 'relation':'project.project', 'domain': [('active','<>',False)]},
}

def _create_duplicate(self, cr, uid, data, context):
    campaign_obj=pooler.get_pool(cr.dbname).get('dm.campaign')
    project_obj = pooler.get_pool(cr.dbname).get('project.project')
    campaign = campaign_obj.browse(cr, uid, data['id'])
    tasks_obj = pooler.get_pool(cr.dbname).get('project.task')
    tasks_ids = tasks_obj.search(cr, uid, [('project_id','=',data['form']['project_id'])])
    duplicate_project_id= project_obj.copy(cr, uid,data['form']['project_id'], {'active': True})

    for task in tasks_obj.browse(cr, uid, tasks_ids):

        if task.type:
            if task.type.name == 'DTP' and campaign.dtp_responsible_id:
                new_tasks_id = tasks_obj.copy(cr, uid, task.id, {'project_id':duplicate_project_id,'user_id':campaign.dtp_responsible_id.id,'state':'open'})
            elif task.type.name == 'Mailing Manufacturing' and campaign.manufacturing_responsible_id:
                new_tasks_id = tasks_obj.copy(cr, uid, task.id, {'project_id':duplicate_project_id,'user_id':campaign.manufacturing_responsible_id.id,'state':'open'})
            elif task.type.name == 'Customers List' and campaign.files_responsible_id:
                new_tasks_id = tasks_obj.copy(cr, uid, task.id, {'project_id':duplicate_project_id,'user_id':campaign.files_responsible_id.id,'state':'open'})
            else:
                new_tasks_id = tasks_obj.copy(cr, uid, task.id, {'project_id':duplicate_project_id,'state':'open'})
        else:
            new_tasks_id = tasks_obj.copy(cr, uid, task.id, {'project_id':duplicate_project_id,'state':'open'})

    print "Project Date : ",campaign.date_start
    print "Project Dat typee : ",type(campaign.date_start)


    project_obj.write(cr, uid, duplicate_project_id, {'name': project_obj.browse(cr, uid, duplicate_project_id, context).name + " for " + campaign.name})
#    project_obj.write(cr, uid, duplicate_project_id, {'name': project_obj.browse(cr, uid, duplicate_project_id, context).name + " for " + campaign.name,
#                                                        'date_end': campaign.date_start})
    campaign_obj.write(cr, uid, [data['id']], {'project_id': duplicate_project_id})
    return {}

class wizard_campaign_project(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':parameter_form, 'fields': parameter_fields, 'state':[('end','Cancel'),('done', 'Ok')]}

        },
        'done':{
                'actions':[_create_duplicate],
                'result' : {'type':'state', 'state':'end'}
                }
    }
wizard_campaign_project('campaign.project')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

