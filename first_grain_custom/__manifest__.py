# -*- coding: utf-8 -*-
{
    'name': "First Grain Customization",

    'summary': """
        First Grain Customs""",

    'description': """
        First Grain Customs By White Code
    """,

    'author': "Zienab Abd EL Nasser",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',
    'depends':['sale','account_budget','account','purchase','gamification','mail','stock','sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/product_template_view.xml',
        'views/budget.xml',
        'views/account_invoice.xml',
        'views/contract_view.xml',
        'views/operation_logistic_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/bill_leading_view.xml',
        'views/sale_config.xml',
        'views/purchase_order_view.xml',
        'views/customer_payment_view.xml',
        'views/form4_view.xml',
        'views/cbot_view.xml',
    ],
}