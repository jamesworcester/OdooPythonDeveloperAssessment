{
    "name": "Account Vendor Bill Admin Notes",
    "version": "18.0.1.0.0",
    "author": "James Worcester",
    "contributors": ["James Worcester"],
    "license": "Other proprietary",
    "images": [],
    "category": "Accounting",
    "website": "",
    "summary": "Account Vendor Bill Admin Notes",
    "description": """
Account Vendor Bill Admin Notes
===============================
* Add a new checkbox field labelled 'Internal Only' in the Vendor Bill chatter when the 'Log note' button is pressed
* When the 'Internal Only' checkbox is checked, once the note is logged it will only be visible to users in the 
'Invoicing/Administrator' group ('account.group_account_manager')
* When the 'Internal Only' checkbox is unchecked, once the note is logged it will be visible to all users who have 
access to the Vendor Bill
""",
    "depends": [
        "base",
        "web",
        "account",
        "mail",
    ],
    "data": [
        "security/mail_security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mail/static/src/core/common/composer.js",
            "mail/static/src/core/common/composer.xml",
            "account_vendor_bill_admin_notes/static/src/js/composer.xml",
            "account_vendor_bill_admin_notes/static/src/js/composer.js",
            "account_vendor_bill_admin_notes/static/src/js/thread_model_patch.js",
        ],
    "installable": True,
    "application": False,
    "auto_install": False,
    }
}