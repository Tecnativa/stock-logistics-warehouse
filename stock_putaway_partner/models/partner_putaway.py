# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models


class ProductPutawayStrategy(models.Model):
    _inherit = 'product.putaway'

    @api.model
    def _get_putaway_options(self):
        ret = super(ProductPutawayStrategy, self)._get_putaway_options()
        return ret + [('per_partner', 'Fixed per partner location')]

    partner_location_ids = fields.One2many(
        comodel_name='stock.partner.putaway.strategy',
        inverse_name='putaway_id',
        string='Fixed per partner location',
        copy=True)
    method = fields.Selection(selection=_get_putaway_options)

    @api.model
    def putaway_apply(self, putaway_strategy, product):
        if putaway_strategy.method == 'per_partner':
            strategy_domain = [
                ('putaway_id', '=', putaway_strategy.id),
                # ('product_product_id', '=', product.id),
            ]
            for strategy in putaway_strategy.partner_location_ids.search(
                    strategy_domain, limit=1):
                return strategy.fixed_location_id.id
        else:
            return super(ProductPutawayStrategy, self).putaway_apply(
                putaway_strategy, product)


class StockPartnerPutawayStrategy(models.Model):
    _name = 'stock.partner.putaway.strategy'
    _rec_name = 'partner_id'
    _order = 'putaway_id, sequence'

    _sql_constraints = [(
        'putaway_partner_location_unique',
        'unique(putaway_id,partner_id,fixed_location_id)',
        _('There is a duplicate location by put away assignment!')
    )]

    putaway_id = fields.Many2one(
        comodel_name='product.putaway',
        string='Put Away Strategy',
        required=True,
        select=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        select=True,
        required=True)
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')])
    sequence = fields.Integer()
