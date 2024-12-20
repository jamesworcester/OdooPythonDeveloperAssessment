{
    "name": "Account Vendor Bill API",
    "version": "18.0.1.0.0",
    "author": "James Worcester",
    "contributors": ["James Worcester"],
    "license": "Other proprietary",
    "images": [],
    "category": "Accounting",
    "website": "",
    "summary": "Account Vendor Bill API",
    "description": """
Account Vendor Bill API
=======================
* Add a GET API endpoint at '/api/v1/bills' that returns all posted Vendor Bills in JSON format
* Returns the number of bills as 'count' (int)
* Returns the list of posted Vendor Bills as 'data' (list)
* Each returned Vendor Bill contains key-value pairs for its 'name' (str) and 'total_amount' (float)
* An LRU cache is used to store the Vendor Bills in JSON format
* The cache is invalidated when a Vendor Bill is written to or created

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
""",
    "depends": [
        "account",
    ],
    "data": [
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}