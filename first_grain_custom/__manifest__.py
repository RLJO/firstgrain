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
    'depends':['sale','account_budget','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/budget.xml',
        'views/account_invoice.xml'
    ],
}