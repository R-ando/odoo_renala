# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil import relativedelta
from openerp import api, models, fields, tools

# TODO make related field instead

class RepportPayslipOstie(models.Model):
    _name = "etat.ostie"
    _description = "Etat ostie"
    _auto = False

    payslip_id = fields.Many2one('hr.payslip', string=u'Bulletin')
    employee = fields.Char(u'Employé', size=128)
    num_emp = fields.Char('Matricule', size=128)
    basic = fields.Float('Salaire de base')
    omsi = fields.Float('OSTIE Travailleur')
    omsiemp = fields.Float('OSTIE Employeur')
    brut = fields.Float('Salaire Brut')
    date_from = fields.Date()
    date_to = fields.Date()

    @api.model_cr
    def init(self):
        cotisation_sante_patr = self.env['res.company'].search([('write_uid', '=', self.env.uid)], limit=1).mapped('cotisation_sante_patr')

        if cotisation_sante_patr:
            tools.drop_view_if_exists(self._cr, 'etat_ostie')
            self._cr.execute("""
                        CREATE OR REPLACE VIEW etat_ostie AS (
                        SELECT 
                        p.id,
                        p.id as payslip_id,
                        emp.num_emp as num_emp,
                        line_brut.amount as brut, 
                        line_basic.amount as basic,
                        (line_net.amount* 2)/100 as omsi,  
                        line_net.amount/100 as omsiemp,
                        p.date_from as date_from,
                        p.date_to as date_to,
                        (CASE WHEN emp.name_related is not NULL
                          THEN CONCAT(upper(emp.first_name ),' ',emp.name_related)
                          ELSE emp.name_related
                          END) as employee 
                        from hr_payslip p
                        LEFT JOIN hr_payslip_line line_basic on  line_basic.slip_id = p.id and line_basic.code = 'BASIC'
                        LEFT JOIN hr_payslip_line line_net on  line_net.slip_id = p.id and line_net.code = 'NET'
                        LEFT JOIN hr_payslip_line line_brut on  line_brut.slip_id = p.id and line_brut.code = 'GROSS'
                        INNER JOIN hr_employee emp on emp.id = p.employee_id
                        WHERE p.state = 'done' 
                        )
                    """)
        else:
            pass