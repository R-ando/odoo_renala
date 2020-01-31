# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, _
from datetime import datetime, date

class Employee(models.Model):
    _inherit = 'hr.employee'
    _name = 'hr.employee'

    first_name = fields.Char(string="Prenom", size=128, required=False)
    num_cnaps_emp = fields.Char(string="N° CNAPS")
    num_cin = fields.Char(string="N° CIN", size=10)
    date_cin = fields.Date(string='Date CIN')
    lieu_cin = fields.Char(string='Lieu de délivrance CIN')
    num_emp = fields.Char(string="N° Matricule")
    nombre_enfant_cnaps = fields.Integer(string=u"Nombre d'enfant allouée CNaPS", required=True)
    seniority = fields.Char(string=u'Ancienneté', compute='get_seniority')
    #make field obligatory
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], groups='hr.group_hr_user', required=True)
    birthday = fields.Date('Date of Birth', groups='hr.group_hr_user',  required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    job_id = fields.Many2one('hr.job', string='Job Title', required=True)
    #percpt_minimum = fields.Float(string='Perception minimum', default=2000)

    def if_exist(self, name):
        if not name:
            return ''
        else:
            return name
    @api.multi
    def name_get(self):
        data = []
        for employee in self:
            name = self.if_exist(employee.name_related).upper() + ' ' + self.if_exist(employee.first_name)
            data.append((employee.id, name))
        return data

    @api.multi
    def get_seniority(self):
        for employee in self:
            date_start = self.env['hr.contract'].search([('employee_id', '=', employee.id)]).mapped('date_start')
            if date_start:
                date_start_ = datetime.strptime(date_start[0], tools.DEFAULT_SERVER_DATE_FORMAT)
                dif_m = self.diff_month(date.today(), date_start_)
                if dif_m < 13:
                    if dif_m == 12:
                        employee.seniority = '1 ans'
                    elif dif_m == 0:
                        d0 = date(date_start_.year, date_start_.month, date_start_.day)
                        employee.seniority = str(date.today() - d0).replace('day, 0:00:00', ' jours ')
                    else:
                        employee.seniority = str(dif_m) + ' mois'
                else:
                    mois = dif_m % 12
                    ans = (dif_m - mois) / 12
                    employee.seniority = str(ans) + 'ans/' + str(mois) + 'mois'
            else:
                employee.seniority = '0'


    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
