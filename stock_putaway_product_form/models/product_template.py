# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Víctor Martínez - Tecnativa

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tmpl_putaway_ids = fields.One2many(
        comodel_name="stock.putaway.rule",
        inverse_name="product_tmpl_id",
        string="Product putaway strategies by product",
    )

    product_putaway_categ_ids = fields.Many2many(
        comodel_name="stock.putaway.rule",
        string="Product putaway strategies by category",
        compute="_compute_putaway_categ_ids",
    )

    def _get_categ_and_parents(self, categ):
        parent_categ_iterator = categ
        res = self.env["product.category"]
        while parent_categ_iterator:
            res += parent_categ_iterator
            parent_categ_iterator = parent_categ_iterator.parent_id
        return res

    @api.depends("categ_id")
    def _compute_putaway_categ_ids(self):
        """Pay attention to keep only 1 (most specific,
        i.e closest to our product category's parents)
        putaway.strat per product.putaway"""
        for rec in self:
            categ = rec.categ_id
            categs = self._get_categ_and_parents(categ)
            # get matching lines from our category or its parents
            rules = self.env["stock.putaway.rule"].search(
                [("category_id", "in", categs.ids)]
            )
            rec.product_putaway_categ_ids = rules
