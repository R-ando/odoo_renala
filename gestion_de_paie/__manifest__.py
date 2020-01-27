# -*- coding: utf-8 -*-
{
    'name': 'Paie Malagasy',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 0,
    'description': """Gestion de paie Malagasy""",
    'website': 'https://www.ingenosya.mg',
    'depends': ['hr_contract', 'hr_payroll', 'base', 'report', 'resource', 'hr_holidays', 'web', 'l10n_mg_partner'],
    'data': ['security/ir.model.access.csv',
             'report/report_etat_payslip.xml',

             'views/paie_view.xml',
             'views/etat_salaire_view.xml',
             'views/cnaps_view.xml',
             'views/ostie_view.xml',
             'views/irsa_view.xml',
             'views/employee_view.xml',
             'views/company_view.xml',
             'views/payment_view.xml',
             'views/hr_holidays_view.xml',
             'views/etat_payslip_view.xml',
             'views/resources.xml',
             'views/message_pop_view.xml',
             'data/gestion_de_paie_data.xml',

             'report/report_paie_templates.xml',
             'report/report_paie.xml',
             'report/report_cnaps_templates.xml',
             'report/report_cnaps.xml',
             'report/report_ostie_templates.xml',
             'report/report_ostie.xml',
             'report/report_irsa_templates.xml',
             'report/report_irsa.xml',
             'report/report_etat_salaire_templates.xml',
             'report/report_etat_salaire.xml',
             'report/report_etat_ostie.xml',
             'report/report_etat_cnaps.xml',
             'report/report_etat_irsa.xml',
             'report/report_test.xml',
             'wizard/cnaps_wizard_view.xml',
             'wizard/ostie_wizard_view.xml',
             'wizard/irsa_wizard_view.xml',
             #'security/group_security_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
