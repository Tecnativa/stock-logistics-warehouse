# Copyright 2017 FactorLibre - Janire Olagibel <janire.olegibel@factorlibre.com>
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models

_LINE_KEYS = ["product_id", "product_uom_qty"]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        old_lines = self.mapped("order_line")
        dict_old_lines = {}
        for line in old_lines:
            dict_old_lines[line.id] = {
                "product_id": line.product_id,
                "product_uom_qty": line.product_uom_qty,
            }
        res = super().write(vals)
        for order in self:
            body = ""
            for line in vals.get("order_line", []):
                if line[0] == 1 and list(set(line[2].keys()).intersection(_LINE_KEYS)):
                    body += order.get_message(dict_old_lines.get(line[1]), line[2])
            if body != "":
                order.message_post(body=body)
        return res

    @api.model
    def get_message(self, old_vals, new_vals):
        ProductProduct = self.env["product.product"]
        body = _("<p>Modified Order line data</p>")
        if "product_id" in new_vals:
            old_product = old_vals["product_id"].display_name
            new_product = ProductProduct.browse(new_vals["product_id"]).display_name
            body += _("<div>     <b>Product</b>: ")
            body += "{} → {}</div>".format(old_product, new_product)
        if "product_uom_qty" in new_vals:
            if "product_id" not in new_vals:
                body += _("<div>     <b>Product</b>: %s") % (
                    old_vals["product_id"].display_name
                )
            body += _("<div>     <b>Product qty.</b>: ")
            body += "{} → {}</div>".format(
                old_vals["product_uom_qty"], float(new_vals["product_uom_qty"]),
            )
        body += "<br/>"
        return body


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_readonly = fields.Boolean(compute="_compute_is_readonly", store=False)

    @api.depends("order_id.state", "reservation_ids")
    def _compute_is_readonly(self):
        for line in self:
            line.is_readonly = (
                len(line.reservation_ids) > 0 or line.order_id.state != "draft"
            )
