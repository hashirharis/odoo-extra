# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import os

import pooler
from tools.translate import _
from base_module_quality import base_module_quality
from tools import config


class quality_test(base_module_quality.abstract_quality_check):

    def __init__(self):
        super(quality_test, self).__init__()
        self.name = _("Structure Test")
        self.note = _("""
This test checks if the module satisfy tiny structure
""")
        self.bool_installed_only = False
        self.ponderation = 1.0
        self.result_dict = {}
        return None

    def run_test(self, cr, uid, module_path):
        a = len(module_path.split('/'))
        module_name = module_path.split('/')
        module_name = module_name[a-1]
        list_files = os.listdir(module_path)
        f_list = []
        module_dict = {}
        module_dict['module'] = []
        n = 0
        final_score = 0.0
        for file in list_files:
            if file.split('.')[-1] != 'pyc':
                path = os.path.join(module_path, file)
                if file=='wizard' and os.path.isdir(path):
                    module_dict[file] = []
                if file=='report' and os.path.isdir(path):
                    module_dict[file] = []
                if file=='security' and os.path.isdir(path):
                    module_dict[file] = []
                module_dict['module'].append(file)
                f_list.append(file)
        for i in f_list:
            path = os.path.join(module_path, i)
            if os.path.isdir(path) and not i=='i18n':
                for j in os.listdir(path):
                    if i in ['report', 'wizard', 'security', 'module'] and j.split('.')[-1] != 'pyc':
                        module_dict[i].append(j)
                        f_list.append(os.path.join(i, j))

        # module files calculation (module.py,module_view.xml,etc..)
        com_list = ['_unit_test.xml', '.py', '_view.xml', '_workflow.xml' , '_wizard.xml', '_report.xml', '_data.xml', '_demo.xml', '_security.xml', '_sequence.xml']
        com_list = map(lambda x: module_name+x, com_list)
        main_file = ['__init__.py', '__terp__.py']
        com_list.extend(main_file)
        module_dict['module'] = filter(lambda x: len(x.split("."))>1,module_dict['module'])
        score = self.get_score(module_dict['module'], com_list)
        n = n + 1
        final_score += score

        # report folder checking...
        if module_dict.has_key('report'):
            report_pys = filter(lambda x: x.split('.')[1]=='py' and x!='__init__.py',module_dict['report'])
            report_pys = map(lambda x:x.split('.')[0],report_pys)
            reports = ['.sxw', '.rml', '.xsl', '.py', '.xml']
            org_list_rep = []
            for l in report_pys:
                for r in reports:
                    org_list_rep.append(l+r)
            org_list_rep.append('__init__.py')
            score_report = self.get_score(module_dict['report'], org_list_rep, 'report/')
            n = n + 1
            final_score += score_report

        # wizard folder checking...
        if module_dict.has_key('wizard'):
            wizard_pys = filter(lambda x: x.split('.')[1]=='py' and x!='__init__.py',module_dict['wizard'])
            wizard_pys = map(lambda x:x.split('.')[0], wizard_pys)
            wizards = ['_view.xml', '_workflow.xml', '.py']
            org_list_wiz = []
            for l in wizard_pys:
                for r in wizards:
                    org_list_wiz.append(l+r)
            org_list_wiz.append('__init__.py')
            score_wizard = self.get_score(module_dict['wizard'], org_list_wiz, 'wizard/')
            n = n + 1
            final_score += score_wizard

        # security folder checking...
        if module_dict.has_key('security'):
            security = [module_name + '_security.xml']
            security.extend(['ir.model.access.csv'])
            score_security = self.get_score(module_dict['security'], security, 'security/')
            n = n + 1
            final_score += score_security

        # final score
        self.score = float(final_score) / n
        self.result = self.get_result({ module_name: [module_name, int(self.score*100)]})
        self.result_details += self.get_result_details(self.result_dict)
        return None

    def get_result(self, dict):
        header = ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-10s \n', [_('Module Name'), _('Result'),])
        if not self.error:
            return self.format_table(header, data_list=dict)
        return ""

    def get_score(self, module_list, original_files, mod_folder=''):
        score = 0
        module_length = len(module_list)
        for i in module_list:
            if i in original_files:
                score += 1
            else:
                if mod_folder != 'wizard/':
                    self.result_dict[i] = [mod_folder + i,'File name does not follow naming standards.']
                    score -= 1
                    module_length -= 1
        score = float(score) / float(module_length)
        return score

    def get_result_details(self, dict):
        str_html = '''<html><head></head><body><table border="1">'''
        header = ('<tr><th>%s</th><th>%s</th></tr>',[_('File Name'),_('Feedback about structure of module')])
        if not self.error:
           res = str_html + self.format_html_table(header, data_list=dict) + '</table></body></html>'
           return res
        return ""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
