import json
from odoo import http
from odoo.http import request, Response


class AccountVendorBillAPI(http.Controller):
    @http.route('/api/v1/bills', auth='user', methods=['GET'])
    def get_vendor_bills(self):
        """ Get cached vendor bills in JSON format

        Example Response:
        -----------------
        {
            "count": 3,
            "data": [
                {"name": "BILL/2024/1", "total_amount": 1545.54},
                {"name": "BILL/2024/2", "total_amount": 3455.45},
                {"name": "BILL/2024/3", "total_amount": 9800.56}
            ]
        }
        """
        headers_json = {'Content-Type': 'application/json'}
        cached_vendor_bills_response = request.env['account.move'].get_cached_vendor_bills()
        return Response(json.dumps(cached_vendor_bills_response), headers=headers_json)