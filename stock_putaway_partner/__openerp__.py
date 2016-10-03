# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Putaway strategy per partner',
    'summary': 'Set a product location and put-away strategy per product',
    'version': '9.0.1.0.0',
    'category': 'Inventory',
    'website': 'http://www.tecnativa.com',
    'author':
        'Tecnativa, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'stock'
    ],
    'data': [
        'views/res_partner.xml',
        'views/partner_putaway.xml',
        'security/ir.model.access.csv',
    ],
}
