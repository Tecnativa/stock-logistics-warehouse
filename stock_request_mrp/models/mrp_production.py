# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    stock_request_ids = fields.Many2many(
        "stock.request",
        "mrp_production_stock_request_rel",
        "mrp_production_id",
        "stock_request_id",
        string="Stock Requests",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("stock_request_ids")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_count = len(rec.stock_request_ids)

    def _get_stock_requests(self):
        """Get all stock requests from action (allows inheritance by other modules)."""
        return self.mapped("stock_request_ids")

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request.action_stock_request_form"
        )
        requests = self._get_stock_requests()
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
    ):
        """Inject stock request allocations when creating the finished move."""
        res = super()._get_move_finished_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            byproduct_id=byproduct_id,
        )
        if self.stock_request_ids:
            res["allocation_ids"] = [
                (
                    0,
                    0,
                    {
                        "stock_request_id": request.id,
                        "requested_product_uom_qty": product_uom_qty,
                    },
                )
                for request in self.stock_request_ids
            ]
        return res

    def _action_cancel(self):
        """Añadimos excepcion a stock.request o stock.request.order."""
        res = super()._action_cancel()
        self._exception_on_stock_request()
        return res

    def _get_all_sources(self):
        """Método para obtener el primer parent."""
        res = self.env["mrp.production"]
        for item in self:
            for source in item._get_sources():
                res += source
                res += source._get_all_sources()
        return res

    def _exception_on_stock_request(self):
        """Agrupamos por stock.request o stock.request.order con todas
        las fabricaciones. Necesitamos obtener la fabricacion padre para que aplique
        si se cancela una fabricación de nivel 3 por ejemplo."""
        requests_info = {}
        request_orders_info = {}
        production_model = self.env["mrp.production"]
        for item in self:
            sources = item._get_all_sources() or item
            for request in sources.stock_request_ids:
                if request.order_id:
                    if request.order_id not in request_orders_info:
                        request_orders_info[request.order_id] = production_model
                    request_orders_info[request.order_id] += item
                else:
                    if request not in requests_info:
                        requests_info[request] = production_model
                    requests_info[request] += item
        # stock.request
        for request, productions in requests_info.items():
            request._log_exception_from_manufacture(productions)
        # stock.request.order
        for order, productions in request_orders_info.items():
            order._log_exception_from_manufacture(productions)
