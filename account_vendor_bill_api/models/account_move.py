from odoo import models
from functools import lru_cache

class AccountMove(models.Model):
    _inherit = 'account.move'

    @lru_cache(maxsize=None)
    def get_cached_vendor_bills(self, move_type='in_invoice', state='posted'):
        """ Return and cache all posted vendor bills in JSON format

        Explanation of caching decisions:
            Reasons for using an LRU cache instead of an attachment cache that is stored and refreshed periodically (e.g hourly):
                1. By ensuring changes to the underlying data invalidate the cache, we can ensure the API endpoint always serves accurate and
                up-to-date data to the client
                2. A periodic refresh of the cache would lead to the endpoint often serving inaccurate data to the client
                3. Inaccurate data being served by the client will lead to decisions being made based on incorrect data
                4. If the client is served inaccurate data, a warning should be communicated with that data to users of the endpoint
                5. By avoiding periodic refreshing, we avoid scenarios where the cache is refreshed when the data is already up to date,
                saving system resources
                6. By avoiding periodic refreshing, we avoid unnecessary system complexity and points of failure as we do not need to
                implement logic or an additional cronjob to refresh the cache, saving system resources

            Explanation of lru_cache decisions:
                1. A maxsize of None is used to ensure the cache can store all posted Vendor Bills
                2. create: The cache is only invalidated when a Vendor Bill ('in_invoice') is created. We do not want to invalidate the cache
                when another type of account.move is created
                3. write: The cache is only invalidated when a Vendor Bill ('in_invoice') is written to. We do not want to invalidate the
                cache when another type of account.move is written to

        """
        cached_vendor_bills = self.search([
            ('move_type', '=', move_type),
            ('state', '=', state),
        ])

        cached_vendor_bills_response = {
            'count': len(cached_vendor_bills),
            'data': [
                {
                    'name': bill.name,
                    'total_amount': f"{bill.amount_total:.2f}"
                }
                for bill in cached_vendor_bills
            ]
        }

        return cached_vendor_bills_response

    def create(self, vals_list):
        """ Override the create method to invalidate the cache if a Vendor Bill is created"""
        if vals_list.get('move_type') == 'in_invoice':
            self.get_cached_vendor_bills.cache_clear()
        return super().create(vals_list)

    def write(self, vals):
        """ Override the write method to invalidate the cache if a Vendor Bill is written to"""
        for record in self:
            if record.move_type == 'in_invoice':
                self.get_cached_vendor_bills.cache_clear()
        return super().write(vals)