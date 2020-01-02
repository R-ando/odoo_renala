# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ReportPayslipIrsa(models.Model):
    _name = "etat.irsa"
    _description = "Etat irsa"
    _auto = False

    payslip_id = fields.Many2one('hr.payslip', string=u'Employé')
    num_emp = fields.Char('Matricule', size=128)
    employee = fields.Char(u'Employé', size=128)
    date_from = fields.Date()
    date_to = fields.Date()
    brut = fields.Float('Salaire Brut')
    net = fields.Float('Salaire Net')
    irsa = fields.Float('IRSA')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'etat_irsa')
        self._cr.execute("""
            CREATE OR REPLACE VIEW etat_irsa AS (
            SELECT 
                    p.id,
                    p.id as payslip_id,
                    emp.num_emp as num_emp,
                    p.date_from as date_from,
                    p.date_to as date_to,
                    line_brut.amount as brut, 
                    line_net.amount as net,
                    line_irsa.amount as irsa, 
                    (CASE WHEN emp.name_related is not NULL
                      THEN CONCAT(upper(emp.first_name ),' ',emp.name_related)
                      ELSE emp.name_related
                      END) as employee 
                    from hr_payslip p
                    LEFT JOIN hr_payslip_line line_net on  line_net.slip_id = p.id and line_net.code = 'NET'
                    LEFT JOIN hr_payslip_line line_brut on  line_brut.slip_id = p.id and line_brut.code = 'GROSS'
                    LEFT JOIN hr_payslip_line line_irsa on  line_irsa.slip_id = p.id and line_irsa.code = 'IRSA'
                    INNER JOIN hr_employee emp on emp.id = p.employee_id
                    WHERE p.state = 'done'
            )
        """)



