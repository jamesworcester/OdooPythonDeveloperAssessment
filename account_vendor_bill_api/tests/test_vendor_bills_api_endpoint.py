# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestVendorBillsAPIEndpoint(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_x = cls.env['product.product'].create({
            'name': 'Product X',
            'lst_price': 100.0,
            'standard_price': 90.0,
        })

        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Partner A',
            'email': 'abc@abc.com'})

        cls.in_invoice_1 = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'name': 'BILL/2024/1',
            'date': '2024-12-14',
            'invoice_date': '2024-12-14',
            'partner_id': cls.partner_a.id,
            'invoice_line_ids': [],
        })

        cls.in_invoice_line_1 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice_1.id,
            'product_id': cls.product_x.id,
            'quantity': 1,
            'product_uom_id': cls.product_x.uom_id.id,
            'price_unit': 1545.54,

        })

        cls.in_invoice_2 = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'name': 'BILL/2024/2',
            'date': '2024-12-14',
            'invoice_date': '2024-12-14',
            'partner_id': cls.partner_a.id,
            'invoice_line_ids': [],
        })

        cls.in_invoice_line_2 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice_2.id,
            'product_id': cls.product_x.id,
            'quantity': 1,
            'product_uom_id': cls.product_x.uom_id.id,
            'price_unit': 3455.45,

        })

        cls.in_invoice_3 = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'name': 'BILL/2024/3',
            'invoice_date': '2024-12-14',
            'partner_id': cls.partner_a.id,
            'invoice_line_ids': [],
        })

        cls.in_invoice_line_3 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice_3.id,
            'product_id': cls.product_x.id,
            'quantity': 1,
            'product_uom_id': cls.product_x.uom_id.id,
            'price_unit': 9800.56,
        })


    def test_001_response_no_vendor_bills(self):
        self.authenticate('admin', 'admin')
        self.url = '/api/v1/bills'
        # reset all demo vendor bills to draft
        self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]).button_draft()

        response = self.url_open(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'data': []})

    def test_002_response_with_vendor_bills(self):
        self.authenticate('admin', 'admin')
        self.url = '/api/v1/bills'
        # reset all demo vendor bills to draft
        self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]).button_draft()

        self.in_invoice_1.action_post()
        self.in_invoice_2.action_post()
        self.in_invoice_3.action_post()

        response = self.url_open(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assertEqual(response.json()['data'], [
            {"name": "BILL/2024/3", "total_amount": f"{self.in_invoice_3.amount_total}"},
            {"name": "BILL/2024/2", "total_amount": f"{self.in_invoice_2.amount_total}"},
            {"name": "BILL/2024/1", "total_amount": f"{self.in_invoice_1.amount_total}"}
        ])


    def test_003_response_invalidate_on_write(self):
        self.authenticate('admin', 'admin')
        self.url = '/api/v1/bills'
        # reset all demo vendor bills to draft
        self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]).button_draft()

        self.in_invoice_1.action_post()

        response = self.url_open(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['data'], [
            {"name": "BILL/2024/1", "total_amount": f"{self.in_invoice_1.amount_total}"}
        ])

        self.in_invoice_1.button_draft()

        response = self.url_open(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)
        self.assertEqual(response.json()['data'], [])
