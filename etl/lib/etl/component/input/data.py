# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
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
"""
 This component is used to read data.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""


from etl.component import component
import csv


class data(component):
    """
        This is an ETL Component that return python data from a list of dict
    """

    def __init__(self, datas, name='component.input.data', transformer=None):
        """    
        Required  Parameters ::
        datas : Input datas
        
        Extra Parameters ::
        name          : Name of Component.
        transformer   : Transformer object to transform string data into  particular object
       """
        super(data, self).__init__(name=name, transformer=transformer)
        self.datas = datas
        self.name = name
        self.transformer = transformer

    def process(self):
        for d in self.datas:
            yield d, 'main'
        
    def __copy__(self):
        """
        Overrides copy method
        """
        res=data(self.datas, self.name, self.transformer)
        return res
    
def test():
    from etl_test import etl_test
    import etl
    inp_data = etl.component.input.data([
        {'id': 1, 'name': 'Fabien', 'country_id': 3},
        {'id': 2, 'name': 'Luc', 'country_id': 3},
        {'id': 3, 'name': 'Henry', 'country_id': 1}
    ])
    test = etl_test.etl_component_test(inp_data)
    test.check_output([{'country_id': 3, 'id': 1, 'name': 'Fabien'}, {'country_id': 3, 'id': 2, 'name': 'Luc'}, {'country_id': 1, 'id': 3, 'name': 'Henry'}] )
    res=test.output()
    print res
    
if __name__ == '__main__':
    test()