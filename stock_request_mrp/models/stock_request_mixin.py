# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date

from odoo import models


class StockRequestMixin(models.AbstractModel):
    _name = "stock.request.mixin"
    _description = "Stock Request Mixin"

    def _prepare_note_exception_quantity_mo_values(self, productions):
        return {"productions": productions}

    def _log_exception_from_manufacture(self, productions):
        exception = self.env.ref("mail.mail_activity_data_warning")
        if not any(
            self.activity_ids.filtered(lambda x: x.activity_type_id == exception)
        ):
            template = self.env.ref("stock_request_mrp.exception_mrp_cancel")
            note = template._render(
                values=self._prepare_note_exception_quantity_mo_values(productions)
            )
            self.sudo().activity_schedule(
                "mail.mail_activity_data_warning",
                date.today(),
                note=note,
                user_id=self.env.user.id,
            )
