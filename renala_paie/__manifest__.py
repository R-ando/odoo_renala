# -*- coding: utf-8 -*-
{
    'name': "renala_paie",

    'summary': """
        Personnalisation RH & Paie pour RENALA""",

    'description': """
        Personnalisation RH & Paie pour RENALA
    """,

    'author': "Rado - Ingenosya",
    'website': "https://ingenosya.com/",

    'category': 'Human Resources',
    'version': '1.0',

    'depends': ['base', 'gestion_de_paie'],

    'data': [
        # view
        "views/hr_holidays_views.xml",

        # report
        "report/report_paie_templates.xml",

        # data
        "data/hr_payroll_data.xml",
    ],

    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
}
