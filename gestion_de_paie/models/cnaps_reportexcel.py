# -*- coding: utf-8 -*-

from odoo import fields, models, api

DICT_MONTH = {'01': 'Janvier', '02': u'Février', '03': 'Mars',
              '04': 'Avril', '05': 'Mai', '06': 'Juin',
              '07': 'Juillet', '08': 'Aout', '09': 'Septembre',
              '10': 'Octobre', '11': 'Novembre', '12': 'Decembre'}

DICT_TRIM = {
    '1': u'Premier trimestre',
    '2': u'Deuxième trimestre',
    '3': u'Troisième trimestre',
    '4': u'Quatrième trimestre'
}


class CnapsReport(models.TransientModel):
    _name = "cnaps.reportexcel"

    quarter = fields.Selection(string="Trimèstre", selection=[('1', u'Premier trimestre'),
                                                              ('2', u'Deuxième trimestre'),
                                                              ('3', u'Troisième trimestre'),
                                                              ('4', u'Quatrième trimestre')], required=True)

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

    @api.multi
    def generateCnaps_excel(self):
        years_selected = dict(self._fields['annees'].selection).get(self.annees)
        trim = dict(self._fields['quarter'].selection).get(self.quarter)
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_report_cnaps_file?p='
                   + format(self.env.user.partner_id.id) + '&m='
                   + format(self.three_next_month(trim)) + "&c="
                   + format(self.countEff_three_month(trim, years_selected)) + "&y="
                   + format({'y': years_selected})
                   + "&data_month1=" + format(self.cnaps_list(trim, years_selected, 'period1'))
                   + "&data_month2=" + format(self.cnaps_list(trim, years_selected, 'period2'))
                   + "&data_month3=" + format(self.cnaps_list(trim, years_selected, 'period3'))
                   + '&plf=' + format(self.plafond()) + '&comp_inf='
                   + format(self.company_information()) + '&fmfp='
                   + format(self.fmfp_nbMount_list(trim, years_selected))
        }
        return actions

    def three_next_month(self, trim):
        mois = self.quarter_months(trim, '0')
        indice_month = mois['p1'].split('-')[1]
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

    def three_next_month2(self, month_selected):
        keys = DICT_MONTH.keys()
        vals = DICT_MONTH.values()
        indice_month = keys[vals.index(month_selected)]
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

    def period_salary(self, month_selected, years_selected):
        three_month = self.three_next_month2(month_selected)
        month_rank_mth1 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth1'])]
        month_rank_mth2 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth2'])]
        month_rank_mth3 = DICT_MONTH.keys()[DICT_MONTH.values().index(three_month['mth3'])]
        return {
            'period1': years_selected + "-" + month_rank_mth1,
            'period2': years_selected + "-" + month_rank_mth2,
            'period3': years_selected + "-" + month_rank_mth3
        }

    def trim_to_period(self, trim):
        month = DICT_MONTH[trim['p1'].split('-')[1]]
        years = trim['p1'].split('-')[0]
        return self.period_salary(month, years)

    def countEff_three_month(self, trim, years_selected):
        mois = self.quarter_months(trim, years_selected)
        month = DICT_MONTH[mois['p1'].split('-')[1]]
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

    def total_amount_ByMonth(self, period, code):
        listIdpayslip = self.env["hr.payslip"].search(
            [("date_from", "like", period + "%"), ("state", "=", "done")]).mapped('id')
        return sum(self.env['hr.payslip.line'].search(
            [("slip_id", "in", listIdpayslip), ("code", "=", code), ("state", "=", "done")]).mapped(
            'amount'))

    def cnaps_month(self, period):
        data_month = []
        query = """ select hr_employee.name_related, hr_employee.first_name,hr_payslip.date_to,hr_payslip.date_from, hr_payslip_line.amount
                    from hr_payslip  
                    inner join hr_employee on (hr_employee.id = hr_payslip.employee_id) 
                    inner join hr_payslip_line on (hr_payslip.id = hr_payslip_line.slip_id)
                    where hr_payslip.date_from::text like '{}' and hr_payslip_line.code ='NET' and hr_payslip.state ='done' and payslip.credit_note = False order by hr_employee.name_related""".format(
            period + '%')

        self._cr.execute(query)
        for res in self.env.cr.fetchall():
            data_month.append(res)
        return data_month

    def cnaps_code(self, period, code):
        data_month = []
        query = """ select hr_payslip_line.amount
                    from hr_payslip
                    inner join hr_employee on (hr_employee.id = hr_payslip.employee_id) 
                    inner join hr_payslip_line on (hr_payslip.id = hr_payslip_line.slip_id)
                    where hr_payslip.date_from::text like '{}' and hr_payslip_line.code= '{}' and hr_payslip.state ='done' and payslip.credit_note = False order by hr_employee.name_related""".format(
            period + '%',
            code)

        self._cr.execute(query)
        for res in self.env.cr.fetchall():
            data_month.append(res)
        return data_month

    def list_employee(self):
        self.env['hr.payslip'].search([()])
        pass

    def data_month_years(self, month_selected, years_selected, period_n):
        period = self.period_salary(month_selected, years_selected)
        data_month = self.cnaps_month(period[period_n])
        return {i: data_month[i] for i in range(0, len(data_month))}

    def data_code_payslip(self, month_selected, years_selected, period_n):
        period = self.period_salary(month_selected, years_selected)
        mount = {
            'cnaps_pat': self.cnaps_code(period[period_n], 'CNAPS_PAT'),
            'cnaps_emp': self.cnaps_code(period[period_n], 'CNAPS_EMP'),
            'net': self.cnaps_code(period[period_n], 'NET')
        }
        return mount

    def employee_paysslip_list(self, period, period_n, id):
        emp = self.env["hr.employee"].search([("id", "=", id)])
        contract = self.env["hr.contract"].search([("employee_id", "=", id)])
        job = contract.mapped("job_id")
        return {
            'period': period[period_n].replace("-", "") or u'',
            'name': emp.name_related.upper() or u'',
            'first_name': emp.first_name or u'',
            'embauche': contract.mapped('date_start')[0] or u'',
            'debauche': contract.mapped('date_end')[0] or u'',
            'salary': self.sal(self.getsalry_net(period[period_n], id)) or u'',
            'job': job.name or u'',
            'num_cnaps': emp.num_cnaps_emp or u'',
            'num_emp': emp.num_emp or u'',
            'num_cin': emp.num_cin or u'',

        }

    def sal(self, salr):
        if salr != []:
            return salr[0][0];
        else:
            return 0

    def cnaps_list(self, trim, years_selected, period_n):
        mois = self.quarter_months(trim, years_selected)
        month = DICT_MONTH[mois['p1'].split('-')[1]]
        cnaps_emp = []
        period = self.period_salary(month, years_selected)
        listIdpayslip = self.env["hr.payslip"].search(
            [("date_from", "like", period[period_n] + "%"), ("state", "=", "done"),
             ("credit_note", "=", False)]).mapped(
            'employee_id').ids
        if listIdpayslip != []:
            for id in listIdpayslip:
                cnaps_emp.append(self.employee_paysslip_list(period, period_n, id))
        return cnaps_emp

    def getsalry_net(self, period, employee_id):
        # print(employee_id)
        query = """
            SELECT hr_payslip_line.amount
                    from hr_payslip                
                    inner join hr_employee on (hr_employee.id = hr_payslip.employee_id) 
                    inner join hr_payslip_line on (hr_payslip.id = hr_payslip_line.slip_id)
                    where hr_payslip.date_from::text like  '{}' and hr_payslip_line.code = 'NET' and hr_payslip_line.employee_id = '{}' and hr_payslip.state ='done' and hr_payslip.credit_note = False order by hr_employee.name_related""".format(
            period + '%', employee_id)

        self._cr.execute(query)
        sal = self.env.cr.fetchall()
        return sal

    def plafond(self):
        company_obj = self.env['res.company'].search([('partner_id', '=', 1)])
        return {
            'emp': company_obj.mapped('cotisation_cnaps_emp')[0],  # =1
            'patr': company_obj.mapped('cotisation_cnaps_patr')[0],  # =13
            'plf_amount': company_obj.mapped('plafond_cnaps')[0]
        }

    def trimestre(self, month):
        m = int(DICT_MONTH.keys()[DICT_MONTH.values().index(month)])
        if m <= 3:
            return 1
        if m > 3 & m <= 6:
            return 2
        if m > 6 & m <= 9:
            return 3
        if m > 9:
            return 4

    def company_information(self):
        print(self.id)
        partner = self.env['res.partner'].search([("id", "=", 1)])
        conpany = partner.mapped('company_id')
        return {
            'name': self.str2(partner.name),
            'matricule': self.str2(partner.company_id.company_matricule),
            'address': self.str2(conpany.street) + ' ' + self.str2(conpany.street2),
            'tel': self.str2(partner.company_id.phone),
            'email': self.str2(partner.company_id.email),
            'employer_rate': self.str2(self.plafond()['emp']) + '%',
            'worker_rate': self.str2(self.plafond()['patr']) + '%'
        }

    def str2(self, val):
        if val:
            return str(val)
        else:
            return ''

    def plafond(self):
        company_obj = self.env['res.company'].search([('partner_id', '=', 1)])
        return {
            'emp': company_obj.mapped('cotisation_sante_emp')[0],  # =1
            'patr': company_obj.mapped('cotisation_sante_patr')[0],  # =5
            'plf_amount': company_obj.mapped('plafond_cnaps')[0]
        }

    def fmfp_nbMount(self, period):
        total_fmfp = 0
        nb_fmfp = 0
        contract_wage = self.env['hr.contract'].search([('date_start', 'like', period + '%')]).mapped('wage')
        plafond = float(self.plafond()['plf_amount'])
        for n in contract_wage:
            if n > plafond:
                total_fmfp = total_fmfp + n
            else:
                total_fmfp = total_fmfp + plafond
            nb_fmfp += 1
        return {
            'm_fmfp': total_fmfp,
            'nb_fmfp': nb_fmfp
        }

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

    def fmfp_nbMount_list(self, trim, year):
        period = self.trim_to_period(self.quarter_months(trim, year))
        return {
            'fmfp1': self.fmfp_nbMount(period['period1']),
            'fmfp2': self.fmfp_nbMount(period['period2']),
            'fmfp3': self.fmfp_nbMount(period['period3']),
            'seuil_fmfp': self.env['res.company'].search([('partner_id', '=', '1')]).mapped('seuil_fmfp')
        }