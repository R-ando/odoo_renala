# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class HrPayslipReport(models.Model):
    _name = "hr.payslip.report"
    _description = "Etat de paie"
    _auto = False

    employee_id = fields.Many2one("hr.employee", string=u"Employé", readonly=True)
    wage_net = fields.Float(string="Salaire Net", readonly=True)
    date_from = fields.Date(string="Date", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                CREATE OR REPLACE VIEW hr_payslip_report AS (
                    SELECT
                        p.date_from as date_from,
                        emp.id as employee_id,
                        line.amount as wage_net
                        FROM hr_payslip p
                        INNER JOIN hr_employee emp on emp.id = p.employee_id
                        LEFT JOIN hr_payslip_line line on line.slip_id = p.id and line.code = 'NET'
                )
            """)