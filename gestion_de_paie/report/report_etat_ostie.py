# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp import api, models, fields, tools

class RepportPayslipOstie(models.Model):
    _name = "etatostie"
    _description = "Etat ostie"
    employee_id = fields.Many2one("hr.employee", string="Employé", readonly=True)
    basic = fields.Float('Salaire de base', default=2.2)
    num_emp = fields.Char('num emp')
    Related_name = fields.Char('Nom')
    omsi = fields.Float('OSTIE Travailleur')
    omsiemp = fields.Float('OSTIE Employeur')
    brut = fields.Float('Salaire Brut')
    net = fields.Float('Salaire Net')
    totalomsi = fields.Float('TOTAL OMSI')


    def capped_salary(self, salary):
        return salary * 0.1


