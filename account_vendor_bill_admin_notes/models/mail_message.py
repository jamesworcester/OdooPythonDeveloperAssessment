from odoo import fields, models

class Message(models.Model):
    _inherit = 'mail.message'

    vendor_bill_admin_only = fields.Boolean()