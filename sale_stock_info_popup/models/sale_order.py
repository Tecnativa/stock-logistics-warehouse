# Copyright 2020 Tecnativa - Ernesto Tejeda
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_type = fields.Selection(related='product_id.type')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date')
    free_qty_today = fields.Float(compute='_compute_qty_at_date')
    qty_available_today = fields.Float(compute='_compute_qty_at_date')
    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver')
    is_mto = fields.Boolean(compute='_compute_is_mto')
    display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver')

    @api.depends('product_id', 'product_uom_qty', 'qty_delivered', 'state')
    def _compute_qty_to_deliver(self):
        """ Based on _compute_qty_to_deliver method of sale.order.line
            model in Odoo v13 'sale_stock' module.
        """
        for line in self:
            line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
            line.display_qty_widget = (line.state == 'draft'
                                       and line.product_type == 'product'
                                       and line.qty_to_deliver > 0)

    @api.depends('product_id', 'product_uom_qty', 'order_id.commitment_date', 'order_id.date_order')
    def _compute_qty_at_date(self):
        """ Based on _compute_free_qty method of sale.order.line
            model in Odoo v13 'sale_stock' module.

            This version is much simplified due to performance problems while
            using v13 logic in v12 ORM.
        """
        qty_processed_per_product = defaultdict(lambda: 0)
        self.mapped("product_id").read(["qty_available", "free_qty"])
        for line in self:
            scheduled_date = line.env.context.get('to_date', line.order_id.commitment_date or line.order_id.date_order)
            product = line.product_id
            qty_available = product.qty_available
            free_qty = product.free_qty
            qty_processed = qty_processed_per_product[product.id]
            line.scheduled_date = scheduled_date
            line.qty_available_today = qty_available - qty_processed
            line.free_qty_today = free_qty - qty_processed
            qty_processed_per_product[product.id] += line.product_uom_qty

    @api.depends('product_id', 'route_id', 'order_id.warehouse_id',
                 'product_id.route_ids')
    def _compute_is_mto(self):
        """ Based on _compute_is_mto method of
            sale.order.line model in sale_stock Odoo module.
        """
        for line in self:
            line.is_mto = False
            if not line.display_qty_widget:
                continue
            product = line.product_id
            product_routes = line.route_id
            if not product_routes:
                product_routes = (product.route_ids
                                  + product.categ_id.total_route_ids)
            # Check MTO
            mto_route = line.order_id.warehouse_id.mto_pull_id.route_id
            if not mto_route:
                try:
                    warehouse_obj = self.env['stock.warehouse']
                    mto_route = warehouse_obj._find_global_route(
                        'stock.route_warehouse0_mto', _('Make To Order'))
                except UserError:
                    # if route MTO not found in ir_model_data,
                    # we treat the product as in MTS
                    pass
            line.is_mto = mto_route and mto_route in product_routes
