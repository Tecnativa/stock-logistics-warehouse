# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Víctor Martínez - Tecnativa

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_product_putaway_ids = fields.One2many(
        comodel_name="stock.putaway.rule",
        inverse_name="product_id",
        string="Product putaway strategies by product variant",
    )
