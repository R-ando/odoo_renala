# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ReportPayslipCnaps(models.Model):
    _name = "etat.cnaps"
    _description = "Etat cnaps"
    _auto = False

    payslip_id = fields.Many2one('hr.payslip', string=u'Bulletin')
    num_emp = fields.Char('Matricule', size=128)
    employee = fields.Char(u'Employé', size=128)
    basic = fields.Float('Salaire de base')
    cnapspat = fields.Float('CNAPS Travailleur')
    cnapsemp = fields.Float('CNAPS Employeur')
    brut = fields.Float('Salaire Brut')
    date_from = fields.Date()
    date_to = fields.Date()

    @api.model_cr
    def init(self):
        cotisation_cnaps_patr = \
        self.env['res.company'].search([('write_uid', '=', self.env.uid)], limit=1).mapped('cotisation_cnaps_patr')
        if cotisation_cnaps_patr:
            tools.drop_view_if_exists(self._cr, 'etat_cnaps')
            self._cr.execute("""
                CREATE OR REPLACE VIEW etat_cnaps AS (
                SELECT
                p.id,
                p.id as payslip_id,
                emp.num_emp as num_emp,
                line_brut.amount as brut,
                line_basic.amount as basic,
                (line_net.amount*{})/100 as cnapspat,
                line_net.amount/100 as cnapsemp,
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
            """.format(cotisation_cnaps_patr[0]))
        else:
            pass
