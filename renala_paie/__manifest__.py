# -*- coding: utf-8 -*-
{
    'name': "renala_paie",

    'summary': """
        Personnalisation Paie pour RENALA""",

    'description': """
        Personnalisation Paie pour RENALA
    """,

    'author': "Rado - Ingenosya",
    'website': "https://ingenosya.com/",

    'category': 'Human Resources',
    'version': '1.0',

    'depends': ['base', 'gestion_de_paie'],

    'data': [
        # data
        "data/renala_paie_data.xml",
    ],

    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
}
