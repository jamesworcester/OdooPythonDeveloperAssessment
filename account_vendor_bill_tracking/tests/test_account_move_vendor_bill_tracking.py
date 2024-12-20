# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged, TransactionCase
from odoo import Command
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestAccountMove(AccountTestInvoicingCommon, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.curr = cls.company_data['currency']
        cls.product_apple = cls._create_product(
            name='Apple',
            uom_id=cls.uom_unit.id,
            uom_po_id=cls.uom_unit.id,
            lst_price=5.0,
            standard_price=6.0
        )

        cls.product_banana = cls._create_product(
            name='Banana',
            uom_id=cls.uom_unit.id,
            uom_po_id=cls.uom_unit.id,
            lst_price=8.0,
            standard_price=9.0,
        )

        cls.product_carrot = cls._create_product(
            name='Carrot',
            uom_id=cls.uom_unit.id,
            uom_po_id=cls.uom_unit.id,
            lst_price=200.0,
            standard_price=220.0
        )

        cls.in_invoice = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'date': '2024-12-14',
            'invoice_date': '2024-12-14',
            'partner_id': cls.partner_a.id,
            'currency_id': cls.curr.id,
            'invoice_line_ids': [Command.create({})],
        })

        cls.in_invoice_line_1 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice.id,
            'product_id': cls.product_apple.id,
            'quantity': 1,
            'product_uom_id': cls.product_apple.uom_id.id,
            'price_unit': 100,

        })

        cls.in_invoice_line_2 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice.id,
            'product_id': cls.product_banana.id,
            'quantity': 2,
            'product_uom_id': cls.product_banana.uom_id.id,
            'price_unit': 100,

        })

        cls.in_invoice_line_3 = cls.env['account.move.line'].create({
            'move_id': cls.in_invoice.id,
            'product_id': cls.product_carrot.id,
            'quantity': 3,
            'product_uom_id': cls.product_carrot.uom_id.id,
            'price_unit': 100,
        })

    def test_000_vendor_bill_not_in_draft_state(self):
        self.in_invoice.action_post()

        with self.assertRaises(UserError) as e:
            self.in_invoice.write({
                'invoice_line_ids': [
                    Command.update(self.in_invoice_line_1.id, {
                        'product_id': self.product_banana.id,
                        'quantity': 2,
                        'product_uom_id': self.uom_dozen.id,
                        'price_unit': 200,
                    }),
                ]
            })


    def test_001_wrong_account_move_types(self):
        move_types = ['out_invoice', 'out_refund', 'in_refund', 'out_receipt', 'in_receipt']
        for move_type in move_types:
            self.wrong_move_type_invoice = self.env['account.move'].create({
                'move_type': move_type,
                'date': '2024-12-14',
                'invoice_date': '2024-12-14',
                'partner_id': self.partner_a.id,
                'currency_id': self.curr.id,
                'invoice_line_ids': [],
            })

            self.wrong_move_type_invoice_line_1 = self.env['account.move.line'].create({
                'move_id': self.wrong_move_type_invoice.id,
                'product_id': self.product_apple.id,
                'quantity': 1,
                'product_uom_id': self.product_apple.uom_id.id,
                'price_unit': 100,
            })

            self.wrong_move_type_invoice.write({
                'invoice_line_ids': [
                    Command.update( self.wrong_move_type_invoice_line_1.id,{
                        'product_id': self.product_banana.id,
                        'quantity': 2,
                        'product_uom_id': self.product_banana.uom_id.id,
                        'price_unit': 200,
                    }),
                ]
            })
            self.assertEqual(len(self.wrong_move_type_invoice.message_ids), 0)
            self.wrong_move_type_invoice.unlink()

    def test_002_correct_account_move_type(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update( self.in_invoice_line_1.id,{
                    'product_id': self.product_banana.id,
                    'quantity': 2,
                    'product_uom_id': self.uom_dozen.id,
                    'price_unit': 200,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}", '<p>Product Banana: Product: Apple -&gt; Banana, Quantity: 1.0 -&gt; 2.0, UoM: Units -&gt; Dozens, Price: 100.0 -&gt; 200.0</p>')

    def test_003_update_products(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update(self.in_invoice_line_1.id, {
                    'product_id': self.product_banana.id,
                }),
                Command.update(self.in_invoice_line_2.id, {
                    'product_id': self.product_carrot.id,
                }),
                Command.update(self.in_invoice_line_3.id, {
                    'product_id': self.product_apple.id,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}",
                         '<p>Product Banana: Product: Apple -&gt; Banana, Product Carrot: Product: Banana -&gt; Carrot, Product Apple: Product: Carrot -&gt; Apple</p>')

    def test_004_update_quantities(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update(self.in_invoice_line_1.id, {
                    'quantity': 123
                }),
                Command.update(self.in_invoice_line_2.id, {
                    'quantity': 456,
                }),
                Command.update(self.in_invoice_line_3.id, {
                    'quantity': 789,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}",
                         '<p>Product Apple: Quantity: 1.0 -&gt; 123.0, Product Banana: Quantity: 2.0 -&gt; 456.0, Product Carrot: Quantity: 3.0 -&gt; 789.0</p>')

    def test_005_update_uoms(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update(self.in_invoice_line_1.id, {
                    'product_uom_id': self.uom_dozen.id,
                }),
                Command.update(self.in_invoice_line_2.id, {
                    'product_uom_id': self.uom_dozen.id,
                }),
                Command.update(self.in_invoice_line_3.id, {
                    'product_uom_id': self.uom_dozen.id,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}",
                         '<p>Product Apple: UoM: Units -&gt; Dozens, Product Banana: UoM: Units -&gt; Dozens, Product Carrot: UoM: Units -&gt; Dozens</p>')

    def test_006_update_price_units(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update(self.in_invoice_line_1.id, {
                    'price_unit': 123
                }),
                Command.update(self.in_invoice_line_2.id, {
                    'price_unit': 456,
                }),
                Command.update(self.in_invoice_line_3.id, {
                    'price_unit': 789,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}",
                         '<p>Product Apple: Price: 100.0 -&gt; 123.0, Product Banana: Price: 100.0 -&gt; 456.0, Product Carrot: Price: 100.0 -&gt; 789.0</p>')

    def test_007_change_sequence_and_update_some_relevant_and_irrelevant_values(self):
        self.in_invoice.write({
            'invoice_line_ids': [
                Command.update(self.in_invoice_line_2.id, {
                    'sequence': 1,
                    'name': 'Purple Carrot',
                    'discount': 20,
                    'product_id': self.product_carrot.id,
                    'product_uom_id': self.uom_dozen.id,
                    'price_unit': 456,
                }),
                Command.update(self.in_invoice_line_3.id, {
                    'sequence': 2,
                    'name': 'Granny Smith',
                    'discount': 30,
                    'product_id': self.product_apple.id,
                }),
                Command.update(self.in_invoice_line_1.id, {
                    'sequence': 3,
                    'name': 'Royal Gala',
                    'discount': 10,
                    'quantity': 123,
                    'price_unit': 234,
                }),
            ]
        })

        self.assertEqual(len(self.in_invoice.message_ids), 1)
        self.assertEqual(f"{self.in_invoice.message_ids[0].body}",
                         '<p>Product Carrot: Product: Banana -&gt; Carrot, UoM: Units -&gt; Dozens, Price: 100.0 -&gt; 456.0, Product Apple: Product: Carrot -&gt; Apple, Product Apple: Quantity: 1.0 -&gt; 123.0, Price: 100.0 -&gt; 234.0</p>')
