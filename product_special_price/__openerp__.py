# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    "name" : "Product Special Price",
    "version" : "1.0",
    "author" : "Zikzakmedia SL",
    "website": "www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category" : "Generic Modules/Others",
    "description": """
        This module add new field in product, Special Price, and create new price type.
Configure in Sale Shop is available Special Price.
If special price != 0 and less than price, when create new sale order line, use this price.
    """,
    "depends" : [
        "product",
        "sale_multi_shop",
    ],
    "init_xml" : [],
    "update_xml" : [
        "product_data.xml",
        "product_view.xml",
        "sale_view.xml",
    ],
    "active": False,
    "installable": True
}
