# -*- coding: utf-8 -*-
from ast import literal_eval
from os.path import join

from ..models.cnaps_reportexcel import DICT_MONTH, DICT_TRIM
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class OstieReport(models.TransientModel):
    _name = "ostie.reportexcel"

    quarter = fields.Selection(string="Trimèstre", selection=[('1', u'Premier trimestre'),
                                                              ('2', u'Deuxième trimestre'),
                                                              ('3', u'Troisième trimestre'),
                                                              ('4', u'Quatrième trimestre')], required=True)

    annees = fields.Selection(String=u"Années",
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

    @api.multi
    def generateOstie_excel(self):
        years_selected = dict(self._fields['annees'].selection).get(self.annees)
        trim = dict(self._fields['quarter'].selection).get(self.quarter)
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_report_ostie_file?sante='
                   + format(self.ostie_list(trim, years_selected))
                   + '&plf='
                   + format(self.plafond()) + '&comp_inf='
                   + format(self.company_information()) + '&y=' + format(years_selected) + '&eff='
                   + format(self.countEff_three_month(trim, years_selected)) + '&mc='
                   + format(self.month_concerned(trim, years_selected)) + '&plf32='
                   + format(self.plafond_month1_month2_month3(trim, years_selected)) + '&trim='
                   + format(self.trimestre(trim)) + '&eft='
                   + format(self.count_eff_in_tree_month(trim, years_selected))

        }
        return actions

    def quarter_months(self, quarter, years):
        if quarter == u'Premier trimestre':
            return {
                'p1': years + '-01-01',
                'p2': years + '-03-31'
            }
        if quarter == u'Deuxième trimestre':
            return {
                'p1': years + '-04-01',
                'p2': years + '-06-30'
            }
        if quarter == u'Troisième trimestre':
            return {
                'p1': years + '-07-01',
                'p2': years + '-09-30'
            }
        if quarter == u'Quatrième trimestre':
            return {
                'p1': years + '-10-01',
                'p2': years + '-12-31'
            }

    def trim_to_period(self, trim):
        month = DICT_MONTH[trim['p1'].split('-')[1]]
        years = trim['p1'].split('-')[0]
        return self.period_salary(month, years)

    def list_month(self, trim):
        rank_month = trim.split('-')[1]
        month = DICT_MONTH[rank_month]
        return self.period_salary(month)

    def period_to_trim(self, period, month):
        rank_month = int(period[month].split('-')[1])
        if rank_month <= 3:
            return u'Premier trimestre'
        if rank_month > 3 and rank_month <= 6:
            return u'Deuxième trimestre'
        if rank_month < 6 and rank_month <= 9:
            return u'Troisième trimestre'
        if rank_month > 9:
            return u'Quatrième trimestre'

    def three_next_month(self, month_selected):
        keys = DICT_MONTH.keys()
        vals = DICT_MONTH.values()
        indice_month = keys[vals.index(month_selected)]
        three_months = {}
        months = DICT_MONTH
        indice_month = int(indice_month)
        if indice_month <= 9:
            three_months = {'mth1': months.get('0{}'.format(indice_month)),
                            'mth2': months.get('0{}'.format(indice_month + 1)),
                            'mth3': months.get('0{}'.format(indice_month + 2))}
        else:
            three_months = {'mth1': months.get('{}'.format(indice_month)),
                            'mth2': months.get('{}'.format(indice_month + 1)),
                            'mth3': months.get('{}'.format(indice_month + 2))
                            }
        return three_months

    def period_salary(self, month_selected, years_selected):
        three_month = self.three_next_month(month_selected)
        month_rank_mth1 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth1'])]
        month_rank_mth2 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth2'])]
        month_rank_mth3 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth3'])]
        return {
            'period1': years_selected + "-" + month_rank_mth1,
            'period2': years_selected + "-" + month_rank_mth2,
            'period3': years_selected + "-" + month_rank_mth3
        }

    def getsalry_net(self, period, employee_id):
        query = """
            SELECT hr_payslip_line.amount
                    from hr_payslip                  
                    inner join hr_employee on (hr_employee.id = hr_payslip.employee_id) 
                    inner join hr_payslip_line on (hr_payslip.id = hr_payslip_line.slip_id)
                    where hr_payslip.date_from::text like  '{}' and hr_payslip_line.code = 'NET' 
                    and hr_payslip_line.employee_id = '{}' and hr_payslip.state ='done' 
                    and hr_payslip.credit_note = False  order by hr_employee.name_related""".format(
            period + '%', employee_id)

        self._cr.execute(query)
        sal = self.env.cr.fetchall()
        return sal

    def ostie_list(self, quart, years):
        trim = self.quarter_months(quart, years)  #
        ostie_emp = []
        query = """
        SELECT Distinct employee_id from hr_payslip where (date_from > '{}' and date_from < '{}') and state = 'done' and credit_note = False 
        """.format(trim['p1'], trim['p2'])
        self._cr.execute(query)
        listIdpayslip = self.to_list(self.env.cr.fetchall())
        for id in listIdpayslip:
            ostie_emp.append(self.employee_paysslip_list(trim, id))
        return ostie_emp

    def employee_paysslip_list(self, trim, id):
        period = self.trim_to_period(trim)
        emp = self.env["hr.employee"].search([("id", "=", id)])
        contract = self.env["hr.contract"].search([("employee_id", "=", id)])
        job = contract.mapped("job_id")
        return {
            'name': emp.name_related.upper() or u'',
            'prenom': emp.first_name or u'',
            'sexe': self.sex(emp.gender) or u'',
            'date_naiss': self.date_format(emp.birthday) or u'',
            'date_naiss': self.date_format(emp.birthday) or u'',
            'embauche': self.date_format(contract.mapped('date_start')[0]) or u'',
            'debauche': self.date_format(contract.mapped('date_end')[0]) or u'',
            'salary1': self.sal(self.getsalry_net(period['period1'], id)),
            'salary2': self.sal(self.getsalry_net(period['period2'], id)),
            'salary3': self.sal(self.getsalry_net(period['period3'], id)),
            'job': job.name or u'',
            'num_cin': emp.num_cin or u'',
            'num_cnaps': emp.num_cnaps_emp or u'',
            'num_emp': emp.num_emp or u''
        }

    def date_format(self, date):
        if date:
            d = date.split('-')
            return d[2] + '/' + d[1] + '/' + d[0]
        else:
            pass

    def sex(self, sexe):
        if sexe == 'male':
            return 'H'
        else:
            return 'F'

    def sal(self, salr):
        if salr != []:
            return salr[0][0];
        else:
            return 0

    def sal_float(self, salr):
        if salr != []:
            return float(salr[0][0]);
        else:
            return 0

    def plafond(self):
        company_obj = self.env['res.company'].search([('partner_id', '=', 1)])
        return {
            'emp': company_obj.mapped('cotisation_sante_emp')[0],  # =1
            'patr': company_obj.mapped('cotisation_sante_patr')[0],  # =5
            'plf_amount': company_obj.mapped('plafond_cnaps')[0]
        }

    def company_information(self):
        partner = self.env['res.partner'].search([("id", "=", 1)])
        conpany = partner.mapped('company_id')
        return {
            'name': str(partner.name) or u'',
            'matricule': str(partner.company_id.company_matricule) or u'',
            'stat': str(partner.company_id.vat) or u'',
            'address': str(conpany.street + ' ' + conpany.street2) or u'',
            'tel': str(partner.phone) or u'',
            'email': str(partner.email) or u'',
            'employer_rate': str(self.plafond()['emp']) + '%',
            'worker_rate': str(self.plafond()['patr']) + '%'
        }

    def countEff_three_month(self, trim, years_selected):
        quarter = self.quarter_months(trim, years_selected)
        month = DICT_MONTH[quarter['p1'].split('-')[1]]
        period = self.period_salary(month, years_selected)
        count_mth = {
            'count_mth1': str(self.env["hr.payslip"].search_count(
                [("date_from", "like", period['period1'] + "%"), ("state", "=", "done"), ("credit_note", "=", False)])),
            'count_mth2': str(self.env["hr.payslip"].search_count(
                [("date_from", "like", period['period2'] + "%"), ("state", "=", "done"), ("credit_note", "=", False)])),
            'count_mth3': str(self.env["hr.payslip"].search_count(
                [("date_from", "like", period['period3'] + "%"), ("state", "=", "done"), ("credit_note", "=", False)]))
        }
        return count_mth

    def count_eff_in_tree_month(self, quart, years):
        trim = self.quarter_months(quart, years)
        return self.env["hr.payslip"].search_count(
            [("date_from", ">", trim['p1']), ("date_from", "<", trim['p2']), ("state", "=", "done"),
             ("credit_note", "=", False)])

    def month_concerned(self, trim, years_selected):
        quarter = self.quarter_months(trim, years_selected)
        month = DICT_MONTH[quarter['p1'].split('-')[1]]
        period = self.period_salary(month, years_selected)
        return {
            'm1': self.split_(period['period1']),
            'm2': self.split_(period['period2']),
            'm3': self.split_(period['period3']),
        }

    def split_(self, date):
        m = date.split('-')
        return m[1]

    def plafond_month1_month2_month3(self, trim, years_selected):
        sal_plf1 = 0
        sal_plf2 = 0
        sal_plf3 = 0
        quarter = self.quarter_months(trim, years_selected)
        month = DICT_MONTH[quarter['p1'].split('-')[1]]
        period = self.period_salary(month, years_selected)
        listId1 = self.env["hr.payslip"].search(
            [("date_from", "like", period['period1'] + "%"), ("state", "=", "done"),
             ("credit_note", "=", False)]).mapped('employee_id').ids
        listId2 = self.env["hr.payslip"].search(
            [("date_from", "like", period['period2'] + "%"), ("state", "=", "done"),
             ("credit_note", "=", False)]).mapped('employee_id').ids
        listId3 = self.env["hr.payslip"].search(
            [("date_from", "like", period['period3'] + "%"), ("state", "=", "done"),
             ("credit_note", "=", False)]).mapped('employee_id').ids
        plafond = float(self.plafond()['plf_amount'])

        for id1 in listId1:
            if self.sal(self.getsalry_net(period['period1'], id1)) < plafond:
                sal_plf1 = sal_plf1 + self.sal(self.getsalry_net(period['period1'], id1))
            else:
                sal_plf1 = sal_plf1 + plafond
        for id2 in listId2:
            if self.sal(self.getsalry_net(period['period2'], id2)) < plafond:
                sal_plf2 = sal_plf2 + self.sal(self.getsalry_net(period['period2'], id2))
            else:
                sal_plf2 = sal_plf2 + plafond

        for id3 in listId3:
            if self.sal(self.getsalry_net(period['period3'], id3)) < plafond:
                sal_plf3 = sal_plf3 + self.sal(self.getsalry_net(period['period3'], id3))
            else:
                sal_plf3 = sal_plf3 + plafond

        return {
            'p1': sal_plf1, 'p2': sal_plf2, 'p3': sal_plf3
        }

    def trimestre(self, trim):
        quarter = self.quarter_months(trim, '0')
        m = int(quarter['p1'].split('-')[1])
        if m <= 3:
            return 1
        if m > 3 and m <= 6:
            return 2
        if m > 6 and m <= 9:
            return 3
        if m > 9:
            return 4

    def to_list(self, list):
        b = str(list)
        c = b.replace(',)', '')
        d = c.replace('(', '')
        e = d.replace(' ', '')
        return literal_eval(e)

