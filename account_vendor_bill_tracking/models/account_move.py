from odoo import fields, models
from odoo.tools import float_round

class AccountMove(models.Model):
    _inherit = 'account.move'

    line_ids = fields.One2many(tracking=True)

    def write(self, vals):
        """ Override the write method to track draft vendor bill invoice line updates and post them as messages """
        for record in self:
            if record.move_type == 'in_invoice' and record.state == 'draft' and 'invoice_line_ids' in vals:
                lines_updated = record.populate_lines_updated(vals)
                if lines_updated:
                    record.post_tracked_changes(lines_updated)
        return super().write(vals)

    def populate_lines_updated(self, vals):
        """ Populate the invoice lines and fields that are being updated """
        lines_updated = []
        for values in vals['invoice_line_ids']:
            # If the operation is an update (1)
            if values[0] == 1:
                line_id = values[1]
                values_changed = values[2]
                line = self.env['account.move.line'].browse(line_id)
                fields_updated = []
                # precision_rounding using the new uom if it is being updated, otherwise use the existing uom
                correct_rounding = self.env['uom.uom'].browse(values_changed.get('product_uom_id')).rounding if 'product_uom_id' in values_changed else line.product_uom_id.rounding
                if 'product_id' in values_changed:
                    fields_updated.append({
                        'field': 'Product',
                        'old_value': line.product_id.name,
                        'new_value': self.env['product.product'].browse(values_changed.get('product_id')).name
                    })
                if 'quantity' in values_changed:
                    fields_updated.append({
                        'field': 'Quantity',
                        'old_value': line.quantity,
                        'new_value': float_round(values_changed.get('quantity'),
                                                 precision_rounding=correct_rounding)
                    })
                # handle cases where the product_id is being updated and the same product_uom_id value is in values_changed
                if 'product_uom_id' in values_changed and values_changed.get('product_uom_id') != line.product_uom_id.id:
                    fields_updated.append({
                        'field': 'UoM',
                        'old_value': line.product_uom_id.name,
                        'new_value': self.env['uom.uom'].browse(values_changed.get('product_uom_id')).name
                    })
                # handle cases where the product_id is being updated and the same price_unit value is in values_changed
                if 'price_unit' in values_changed and values_changed.get('price_unit') != line.price_unit:
                    fields_updated.append({
                        'field': 'Price',
                        'old_value': line.price_unit,
                        'new_value': float_round(values_changed.get('price_unit'),
                                                 precision_rounding=correct_rounding)
                    })
                if fields_updated:
                    lines_updated.append({
                        'line': line,
                        'header': f"Product {self.env['product.product'].browse(values_changed.get('product_id')).name if values_changed.get('product_id') else line.name}:",
                        'changes': fields_updated
                    })
        return lines_updated

    def post_tracked_changes(self, lines_updated):
        """ Post the tracked changes as a message in the chatter """
        if lines_updated:
            message_post_output = []
            for changed_line in lines_updated:
                message_post_output.append(changed_line['header'])
                for changed_field in changed_line['changes']:
                    message_post_output.append(
                        f"{changed_field['field']}: {changed_field['old_value']} -> {changed_field['new_value']},")
            self.message_post(body=' '.join(message_post_output).rstrip(','))