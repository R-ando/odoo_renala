# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..models.cnaps_reportexcel import DICT_MONTH
from ast import literal_eval


class Irsareport(models.TransientModel):
    _name = "irsa.reportexcel"
    mois = fields.Selection(string="Mois", selection=[('1', 'Janvier'),
                                                      ('2', u'Février'),
                                                      ('3', 'Mars'),
                                                      ('4', 'Avril'),
                                                      ('5', 'Mai'),
                                                      ('6', 'Juin'),
                                                      ('7', 'Juillet'),
                                                      ('8', 'Aout'),
                                                      ('9', 'Septembre'),
                                                      ('10', 'Octobre'),
                                                      ('11', 'Novembre'),
                                                      ('12', 'Decembre')
                                                      ], required=True)
    annees = fields.Selection(String="Années",
                              selection=[('0', '2000'), ('1', '2001'), ('2', '2002'), ('3', '2003'), ('4', '2004'),
                                         ('5', '2005'), ('6', '2006'), ('7', '2007'),
                                         ('8', '2008'),
                                         ('9', '2009'), ('10', '2010'), ('11', '2011'), ('12', '2012'), ('13', '2013'),
                                         ('14', '2014'),
                                         ('15', '2015'), ('16', '2016'),
                                         ('17', '2017'), ('18', '2018'), ('19', '2019'), ('20', '2020'), ('21', '2021'),
                                         ('22', '2022'),
                                         ('23', '2023'), ('24', '2024'),
                                         ('25', '2025'), ('26', '2026'), ('27', '2027'), ('28', '2028'), ('29', '2029'),
                                         ('30', '2030')],
                              required=True)

    def generateIrsa_excel(self):
        month = dict(self._fields['mois'].selection).get(self.mois)
        years = dict(self._fields['annees'].selection).get(self.annees)
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_report_irsa_file?line_irsa=' +
                   format(self.get_lines(month, years)) + '&comp=' +
                   format(self.company_information(month, years))
        }
        return actions

    def three_next_month(self, month_selected):
        keys = DICT_MONTH.keys()
        vals = DICT_MONTH.values()
        indice_month = keys[vals.index(month_selected)]
        months = DICT_MONTH
        indice_month = int(indice_month)
        if indice_month <= 9:
            three_months = {'mth1': months.get('0{}'.format(indice_month))}
        else:
            three_months = {'mth1': months.get('{}'.format(indice_month))}
        return three_months

    def period(self, month, years):
        three_month = self.three_next_month(month)
        month_rank = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth1'])]
        return years + "-" + month_rank

    def company_information(self, month, years):
        partner = self.env['res.partner'].search([("id", "=", 1)])
        conpany = partner.mapped('company_id')
        return {
            'name': str(partner.name) or u'',
            'matricule': str(partner.company_id.company_matricule) or u'',
            'address': str(conpany.street + ' ' + conpany.street2) or u'',
            'tel': str(partner.company_id.phone) or u'',
            'email': str(partner.company_id.email) or u'',
            'm': month,
            'y': str(years)
        }

    def sex(self, sexe):
        if sexe == 'male':
            return 'H'
        if sexe == 'female':
            return 'F'
        else:
            return ''

    def get_lines(self, month, year):
        date_from = self.period(month, year)
        payslips = self.env['hr.payslip'].search([('date_from', 'like', date_from + '%')])
        res_partner = self.env['res.partner']
        contract = self.env['hr.contract']
        res = []
        for payslip in payslips:
            vals = {}
            vals['num_cnaps'] = payslip.mapped('employee_id').num_cnaps_emp
            vals['sex'] = self.sex(payslip.mapped('employee_id').gender)
            vals['name'] = payslip.mapped('employee_id').name_related.upper()
            vals['first_name'] = payslip.mapped('employee_id').first_name
            vals['num_cin'] = payslip.mapped('employee_id').num_cin
            vals['place_of_birth'] = payslip.mapped('employee_id').place_of_birth if False else u''
            for part in res_partner.search([('id', '=', payslip.mapped('employee_id').address_id.id)], limit=1):
                vals['address'] = part.street
                vals['street'] = part.street2
            for cont in contract.search([('id', '=', payslip.mapped('contract_id').id)]):
                vals['date_start'] = cont.date_start
                vals['date_end'] = cont.date_end if False else u''
                vals['wage'] = cont.wage
                vals['job'] = cont.job_id.name
            for line in payslip.line_ids:
                if line.code == 'NET':
                    vals['net'] = line.amount
                if line.code == 'GROSS':
                    vals['gross'] = line.amount
                if line.code == 'CNAPS_EMP':
                    vals['cnaps_emp'] = line.amount
                if line.code == 'OMSI_EMP':
                    vals['osmi_emp'] = line.amount
                if line.code == 'IRSA':
                    vals['irsa'] = line.amount
                    vals['vide'] = ''
            res.append(vals)
        return res
