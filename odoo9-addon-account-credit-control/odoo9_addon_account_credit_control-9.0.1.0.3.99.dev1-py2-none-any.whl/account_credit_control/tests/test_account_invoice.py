# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil import relativedelta

from openerp import fields
from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestAccountInvoice(TransactionCase):
    post_install = True
    at_install = False

    def test_action_cancel(self):
        """
        Test the method action_cancel on invoice
        We will create an old invoice, generate a control run
        and check if I can unlink this invoice
        :return:
        """
        journal = self.env['account.invoice']._default_journal()

        account_type_rec = self.env.ref('account.data_account_type_receivable')
        account = self.env['account.account'].create({
            'code': '400001',
            'name': 'Clients (test)',
            'user_type_id': account_type_rec.id,
            'reconcile': True,
        })

        tag_operation = self.env.ref('account.account_tag_operating')
        account_type_inc = self.env.ref('account.data_account_type_revenue')
        analytic_account = self.env['account.account'].create({
            'code': '701001',
            'name': 'Ventes en Belgique (test)',
            'user_type_id': account_type_inc.id,
            'reconcile': True,
            'tag_ids': [(6, 0, [tag_operation.id])]
        })
        payment_term = self.env.ref('account.account_payment_term_immediate')

        product = self.env['product.product'].create({
            'name': 'Product test'
        })

        policy = self.env.ref('account_credit_control.credit_control_3_time')
        policy.write({
            'account_ids': [(6, 0, [account.id])]
        })

        # There is a bug with Odoo ...
        # The field "credit_policy_id" is considered as an "old field" and
        # the field property_account_receivable_id like a "new field"
        # The ORM will create the record with old field
        # and update the record with new fields.
        # However constrains are applied after the first creation.
        partner = self.env['res.partner'].create({
            'name': 'Partner',
            'property_account_receivable_id': account.id,
        })
        partner.credit_policy_id = policy.id

        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)
        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'journal_id': journal.id,
            'type': 'out_invoice',
            'payment_term_id': payment_term.id,
            'date_invoice': fields.Datetime.to_string(date_invoice),
            'date_due': fields.Datetime.to_string(date_invoice),
        })

        invoice.invoice_line_ids.create({
            'invoice_id': invoice.id,
            'product_id': product.id,
            'name': product.name,
            'account_id': analytic_account.id,
            'quantity': 5,
            'price_unit': 100,
        })

        # Validate the invoice
        invoice.signal_workflow('invoice_open')

        control_run = self.env['credit.control.run'].create({
            'date': fields.Date.today(),
            'policy_ids': [(6, 0, [policy.id])]
        })
        control_run.generate_credit_lines()

        self.assertTrue(len(invoice.credit_control_line_ids), 1)
        control_line = invoice.credit_control_line_ids

        control_marker = self.env['credit.control.marker']
        marker_line = control_marker\
            .with_context(active_model='credit.control.line',
                          active_ids=[control_line.id])\
            ._get_line_ids()

        self.assertIn(control_line, marker_line)

        marker = self.env['credit.control.marker'].create({
            'name': 'to_be_sent',
            'line_ids': [(6, 0, [control_line.id])]
        })
        marker.mark_lines()

        with self.assertRaises(UserError):
            invoice.unlink()
