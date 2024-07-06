# -*- coding: utf-8 -*-
{
    'name': "Susanti Vendor Portal",

    'summary': """
        Vendor Price Submission Portal""",

    'description': """
        This addon is a powerful tool designed to streamline and simplify the process of collecting price offers from vendors.
    """,

    'author': "PT BION DIGITAL INDONESIA",
    'website': "https://www.bionerp.com",

    'category': 'Website/Website',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
        'base', 'product', 'portal', 'sale', 'stock',
        'l10n_id_efaktur',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/vendor_security.xml',
        'views/menuitem.xml',
        'wizard/generate_delivery_order_listing_views.xml',
        'wizard/delivery_invoice_wizard_views.xml',
        'views/product_supplierinfo_views.xml',
        'views/portal_templates.xml',
        'views/product_views.xml',
        'views/delivery_order_listing_views.xml',
        'views/shipment_capacity_views.xml',
        'views/vendor_pricelist_submission_views.xml',
    ],
    
    'assets': {
        'web.assets_frontend': [
            '/susanti_vendor_portal/static/src/js/vendor_price_submission.js',
            '/susanti_vendor_portal/static/src/js/upload_attachment.js',
            '/susanti_vendor_portal/static/src/js/my_vendor_bill_screen.js',
            '/susanti_vendor_portal/static/src/css/attachment_modal.css',
        ]
    },

}
