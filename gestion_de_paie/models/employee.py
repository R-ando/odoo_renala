# -*- coding: utf-8 -*-


from odoo import models, fields, api
from datetime import date, datetime


class Employee(models.Model):
    _inherit = 'hr.employee'
    _name = 'hr.employee'

    first_name = fields.Char(string="Prenom", size=128)
    num_cnaps_emp = fields.Char(string="N° CNAPS")
    num_cin = fields.Char(string="N° CIN", size=10)
    date_cin = fields.Date(string='Date CIN')
    lieu_cin = fields.Char(string='Lieu de délivrance CIN')
    num_emp = fields.Char(string="N° Matricule")
    nombre_enfant_cnaps = fields.Integer(string=u"Nombre d'enfant allouée CNaPS")
    seniority = fields.Char(string=u'Encieneté', compute='get_seniority')

    @api.multi
    def get_seniority(self):
        for employee in self:
            date_start = self.env['hr.contract'].search([('employee_id', '=', employee.id)]).mapped('date_start')[0].split('-')
            if date_start:
                dif_m = self.diff_month(date.today(), datetime(int(date_start[0]), int(date_start[1]), int(date_start[2])))
                if dif_m < 13:
                    if dif_m == 12:
                        employee.seniority = '1 ans'
                    if dif_m == 0:
                        d0 = date(int(date_start[0]), int(date_start[1]), int(date_start[2]))
                        employee.seniority = str(date.today() - d0) + 'jours'
                    else:
                        employee.seniority = str(dif_m) + 'mois'
                else:
                    mois = dif_m % 12
                    ans = (dif_m - mois) / 12
                    employee.seniority = str(ans) + 'ans/' + str(mois) + 'mois'
            else:
                employee.seniority = '0'

    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
