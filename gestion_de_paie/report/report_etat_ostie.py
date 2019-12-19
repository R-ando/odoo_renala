# -*- coding: utf-8 -*-
from odoo import api, models, fields

class RepportPayslipOstie(models.Model):
    _name = "etatostie"
    _description = "Etat ostie"

    payslip_id = fields.Many2one('hr.payslip', string=u'Employé')
    name = fields.Char(required=True)
    num_emp = fields.Char('Matricule', size=128)
    num_cin = fields.Char('CIN', size=128)
    name_related = fields.Char('Nom', size=128)
    basic = fields.Float('Salaire de base')
    omsi = fields.Float('OSTIE Travailleur')
    omsiemp = fields.Float('OSTIE Employeur')
    brut = fields.Float('Salaire Brut')
    net = fields.Float('Salaire Net')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    totalomsi = fields.Float('TOTAL OMSI')
    avantage = fields.Float('Avantage du mois')
    temps_presence = fields.Float('Temps presence')