# -*- coding: utf-8 -*-
# by Rado - Ingenosya

from odoo import models, fields

# 12 months
MONTHS = [
    ('01', 'Janvier'), ('02', u'Février'), ('03', 'Mars'), ('04', 'Avril'), ('05', 'Mai'), ('06', 'Juin'),
    ('07', 'Juillet'), ('08', 'Aout'), ('09', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Decembre')
]
YEARS = [
    ('2000', '2000'), ('2001', '2001'), ('2002', '2002'), ('2003', '2003'), ('2004', '2004'), ('2005', '2005'),
    ('2006', '2006'), ('2007', '2007'), ('2008', '2008'), ('2009', '2009'), ('2010', '2010'), ('2011', '2011'),
    ('2012', '2012'), ('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017'),
    ('2018', '2018'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'),
    ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'), ('2030', '2030')
]


class Irsareport(models.TransientModel):
    _name = "irsa.reportexcel"

    mois = fields.Selection(string="Mois", selection=MONTHS, required=True)
    annees = fields.Selection(String="Années", selection=YEARS, required=True)

    def generateIrsa_excel(self):
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_report_irsa_file?year=' +
                   format(self.annees) + '&month=' +
                   format(self.mois)
        }
        return actions
