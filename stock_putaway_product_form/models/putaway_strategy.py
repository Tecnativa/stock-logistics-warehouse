# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2019 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>

from odoo import fields, models


class PutAwayStrategy(models.Model):
    _inherit = 'product.putaway'

    # Remove product domain to allow to select product templates
    product_location_ids = fields.One2many(domain=[])

    def _get_putaway_rule(self, product):
        rule = super()._get_putaway_rule(product)
        # The putaway rule is obtained from super we do not know if it was for
        # a product variant or a category, so I filter records first per
        # variant and second per template.
        # I assume that the records has been cached and Odoo does not generate
        # a new sql query for this filter records.
        # If there is not rule we only need search by template.
        if self.product_location_ids:
            if rule:
                putaway = self.product_location_ids.filtered(
                    lambda x: x.product_id == product)
                if putaway:
                    return putaway[0]
            putaway = self.product_location_ids.filtered(
                lambda x: x.product_tmpl_id == product.product_tmpl_id and
                not x.product_id)
            if putaway:
                return putaway[0]
        return rule


class FixedPutAwayStrategy(models.Model):
    _inherit = "stock.fixed.putaway.strat"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        ondelete="cascade",
        readonly=False,
        related="product_id.product_tmpl_id",
        store=True
    )
