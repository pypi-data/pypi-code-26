# -*- coding: utf-8 -*-
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Rename column for specific price for keeping backwards compatibility."""
    if not version:
        return
    cr.execute(
        "ALTER TABLE account_analytic_invoice_line "
        "RENAME price_unit TO specific_price"
    )
