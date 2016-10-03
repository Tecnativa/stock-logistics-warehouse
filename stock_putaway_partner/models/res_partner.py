# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPertner(models.Model):
    _inherit = 'res.partner'

    partner_putaway_ids = fields.One2many(
        comodel_name='stock.partner.putaway.strategy',
        inverse_name='partner_id',
        string="Partner stock locations")
