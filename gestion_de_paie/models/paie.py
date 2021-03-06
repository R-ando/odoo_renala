# -*- coding:utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import calendar


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    categorie = fields.Char('Categorie Professionnel', size=64)
    echellon = fields.Char('Echellon', size=64)
    indice = fields.Integer('Indice', size=10)
    horaire_hebdo = fields.Float('Horaire hebdomadaire')
    payment_mode_id = fields.Many2one(string="Mode de paiement", comodel_name="hr.payment.mode")
    custom_hour_bool = fields.Boolean(string="Heure personnalisée", default=True)
    number_of_hours = fields.Float(string="Nombre d'heures", default=173.33)


class res_company(models.Model):
    _inherit = 'res.company'

    seuil_irsa = fields.Float('Seuil d’imposition')
    taux_irsa = fields.Float('Taux IRSA')
    abat_irsa = fields.Float('Abattement IRSA sur P.C', help="Abattement IRSA pour personne à charge")
    cotisation_cnaps_patr = fields.Float('Cotisation Patronale CNAPS')
    cotisation_cnaps_emp = fields.Float(u'Cotisation Employé CNAPS')
    plafond_cnaps = fields.Float('Plafond de la Securite Sociale')
    num_cnaps_patr = fields.Char(u'Numéro CNAPS', size=64)
    cotisation_sante_patr = fields.Float(u'Cotisation Patronale Santé')
    cotisation_sante_emp = fields.Float(u'Cotisation Employé Santé')
    org_sante = fields.Char('Organisme sanitaire', size=64)
    conge_mens = fields.Float(u'Nombre de jour congé  mensuel')
    amount_allocation = fields.Integer('Montant Allocation Familiale')
    siret = fields.Char('SIRET', size=64)
    ape = fields.Char('APE', size=64)
    seuil_fmfp = fields.Float('FMFP', default=1)
    percpt_minimum = fields.Float(string='Perception minimum', default=2000)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    num_cnaps_emp = fields.Char(u'Numéro CNAPS', size=64)
    num_emp = fields.Char(u'Numéro Matricule', size=64)
    num_cin = fields.Char(u'Numéro CIN', size=64)
    percpt_minimum = fields.Float(string='Perception minimum', default=2000)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _name = 'hr.payslip'

    paiement_mode_id = fields.Many2one(related='contract_id.payment_mode_id')
    stc = fields.Boolean(string='STC')
    half_salary = fields.Boolean(string='Demi-salaire', copy=False)
    priornotice = fields.Float(string=u"Préavis", store=True, copy=False)
    base = fields.Float(string="Base", store=True, default='30', copy=False)
    number_days_worked = fields.Float(string="Nombre de jours travaillé", compute='get_number_days_worked')
    missed_days = fields.Float(string="Jours Manqué", store=True)
    average_gross_notice = fields.Float(string=u"SBR moyen préavis", store=True, compute='_compute_average_gross_prv')
    average_gross = fields.Float(string="SBR Moyen", store=True, compute='_compute_average_gross')
    preavis = fields.Float(string="Préavis", default=0.0, copy=False)
    additional_gross = fields.Float(string="SBR additionnel", delault=0.00, copy=False)
    leave_paye = fields.Float(delault=0.00, copy=False)
    rest_leave = fields.Float(string=u"Congé payé", store=True, default=lambda self: self.employee_id.leaves_count)
    seniority = fields.Char("Ancienneté", compute='_compute_seniority')

    # first_name = fields.Char(related='employee_id.first_name')

    @api.model_cr
    def init(self):
        if self:
            thirteen_month = self.env.ref('gestion_de_paie.hr_rule_basic_TM')
            thirteen_month.write({'active': False})
        else:
            pass

    @api.onchange('employee_id')
    def _rest_leave(self):
        if self.employee_id:
            conge_pris = self._get_employee_request_leaves(self.employee_id, self.date_from, self.date_to, True)
            conge_attr = self._get_employee_allocation_leaves(self.employee_id, self.date_from)
            self.rest_leave = conge_attr - conge_pris
        else:
            pass

    @api.onchange('rest_leave')
    def if_onchange_restleave(self):
        self.leave_paye = self.rest_leave

    def get_preavis(self):
        priornotice = self.priornotice
        if self.priornotice < 0:
            priornotice = self.priornotice * -1
        preavis = (self.get_average_gross_notice_funct() * priornotice) / self.base
        return preavis

    @api.depends('missed_days', 'base')
    def get_number_days_worked(self):
        if self.employee_id:
            wd = self.base - self.missed_days
            self.number_days_worked = wd

    def diff_month(self, d1, d2):
        diff = (d1.year - d2.year) * 12 + d1.month - d2.month
        if diff < 0:
            diff = diff * -1
        return diff - 1

    @api.multi
    def get_average_gross_funct(self):
        additional_gross = self.additional_gross
        for payslip in self:
            average_gross = 0.0
            if payslip.employee_id:
                date_start = payslip.env['hr.contract'].search([('employee_id', '=', payslip.employee_id.id)]).mapped(
                    'date_start')
                payslip_line_obj = payslip.env['hr.payslip.line']
                if date_start:
                    date_start = datetime.strptime(date_start[0], tools.DEFAULT_SERVER_DATE_FORMAT)
                    date_to = datetime.strptime(payslip.date_to, tools.DEFAULT_SERVER_DATE_FORMAT)
                    seniority = payslip.diff_month(date_start, date_to)
                    if seniority <= 12 and seniority != 0:
                        payslips = payslip.search(
                            [('employee_id', '=', payslip.employee_id.id), ('date_to', '<', payslip.date_to)])
                        average_gross_done = 0.0
                        for payslip in payslips:
                            if payslip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]).mapped(
                                    'amount'):
                                average_gross_done = average_gross_done + payslip_line_obj.search(
                                    [('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]).mapped('amount')[0]
                        average_gross = (average_gross_done + payslip.additional_gross) / seniority

                    elif seniority > 12:
                        payslip_line_obj_last_year = payslip.search(
                            [('employee_id', '=', payslip.employee_id.id), ('date_to', '<', payslip.date_to)],
                            limit=12)
                        average_gross_last_year = 0.0
                        for payslip_line in payslip_line_obj_last_year:
                            if payslip_line_obj.search(
                                    [('slip_id', '=', payslip_line.id), ('code', '=', 'GROSS')]).mapped(
                                    'amount'):
                                average_gross_last_year += \
                                    payslip_line_obj.search(
                                        [('slip_id', '=', payslip_line.id), ('code', '=', 'GROSS')]).mapped(
                                        'amount')[0]
                        average_gross = (average_gross_last_year + additional_gross) / 12
                    else:
                        average_gross = 0.0
                else:
                    raise UserError(_('la date debut de contrat est vide'))
            else:
                self.average_gross = 0.0
            return average_gross

    def get_average_gross_notice_funct(self):
        average_gross_notice = 0.0
        if self.employee_id:
            date_start = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)]).mapped(
                'date_start')
            payslip_line = self.env['hr.payslip.line']
            if date_start:
                date_start = datetime.strptime(date_start[0], tools.DEFAULT_SERVER_DATE_FORMAT)
                date_to = datetime.strptime(self.date_to, tools.DEFAULT_SERVER_DATE_FORMAT)
                seniority = self.diff_month(date_start, date_to)
                if seniority > 2:
                    payslip2obj = self.search(
                        [('employee_id', '=', self.employee_id.id), ('date_to', '<', self.date_to)], limit=2,
                        order='date_to desc')
                    sum_gross_done_notice = 0.0
                    for payslip in payslip2obj:
                        if payslip_line.search([('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]):
                            sum_gross_done_notice = sum_gross_done_notice + payslip_line.search(
                                [('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]).mapped('amount')[0]
                    average_gross_notice = sum_gross_done_notice / seniority
                elif seniority <= 2 and seniority > 0:
                    sum_gross_done = 0.0
                    payslips = self.search([('employee_id', '=', self.employee_id.id)])

                    for payslip in payslips:
                        if payslip_line.search([('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]):
                            sum_gross_done += \
                                payslip_line.search([('slip_id', '=', payslip.id), ('code', '=', 'GROSS')]).mapped(
                                    'amount')[0]
                    average_gross_notice = (sum_gross_done + self.additional_gross) / seniority
                elif seniority < 0:
                    pass
                    #raise UserError(_("la date de paiement doit être superieur à l'ancienneté"))
                else:
                    average_gross_notice = 0.0
            else:
                raise UserError(_("cet employer n'a pas encore de contrat"))
        else:
            self.average_gross_notice = 0.0
        return average_gross_notice

    # Congé pris et approuvé durant la même période que celle du bulletin
    def _get_employee_request_leaves(self, employee_id, date_from_fiche, date_to_fiche, map=True):
        holidays_obj = self.env['hr.holidays'].search([('employee_id', '=', employee_id.id)], limit=1)
        pris = 0
        date_from_fiche = fields.Datetime.from_string(date_from_fiche)
        date_to_fiche = fields.Datetime.from_string(date_to_fiche)

        for ho in holidays_obj:
            date_from_holidays = fields.Datetime.from_string(ho.date_from)
            date_to_holidays = fields.Datetime.from_string(ho.date_to)

            if ho.type == 'remove':
                # Test if days of leaves is wholly in the current mouth
                if date_from_fiche <= date_from_holidays and date_to_fiche >= date_to_holidays:
                    pris += ho.number_of_days_temp
                # Test if date of leaves is in current month
                elif date_from_holidays <= date_to_fiche and date_to_holidays >= date_from_fiche:
                    if map:
                        # Set the date_from
                        if date_from_holidays <= date_from_fiche:
                            date_from_calcul = date_from_fiche
                        else:
                            date_from_calcul = date_from_holidays
                        # Set the date_to
                        if date_to_holidays <= date_to_fiche:
                            date_to_calcul = date_to_holidays
                        else:
                            date_to_calcul = date_to_fiche
                        # Calculate the number of day leaves in current month
                        pris += (date_to_calcul - date_from_calcul).days + 1
                    else:
                        pris += ho.number_of_days_temp
        return pris

    # Total de l’attribution de congé approuver de la  même période que la génération du bulletin.
    def _get_employee_allocation_leaves(self, employee_id, date_from_fiche):
        holidays_obj = self.env['hr.holidays'].search([('employee_id', '=', employee_id.id)])
        acquis = 0
        month_fiche = fields.Datetime.from_string(date_from_fiche).month
        year_fiche = fields.Datetime.from_string(date_from_fiche).year

        # Check the allocation validate in current month and year
        for ho in holidays_obj:
            if ho.type == 'add' and ho.state == 'validate' and int(
                    ho.allocation_month) == month_fiche and ho.allocation_year == year_fiche:
                acquis += ho.number_of_days_temp

        return acquis

    def get_avance_salaire(self):
        advance_obj = self.env['hr.wage.advance']
        advances = advance_obj.search(['&', '&', '&', ('employee_id', '=', self.employee_id.id), ('state', '=', 'ok'),
                                       ('date', '>=', self.date_from), ('date', '<=', self.date_to)])
        total_advance = 0.0
        for advance in advances:
            total_advance += advance.amount
        return total_advance

    @api.onchange('employee_id', 'date_from')
    def onchange_employee(self):
        res = super(HrPayslip, self).onchange_employee()

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        worked_days_data_list = [
            {'code': 'HS1', 'contract_id': self.contract_id.id, 'name': u'Heures supplémentaires 130%'},
            {'code': 'HS2', 'contract_id': self.contract_id.id, 'name': u'Heures supplémentaires 150%'},
            {'code': 'HMNUIT', 'contract_id': self.contract_id.id, 'name': u'Heures majorées nuit'},
            {'code': 'HMDIM', 'contract_id': self.contract_id.id, 'name': u'Heures majorées dimanche'},
            {'code': 'HMJF', 'contract_id': self.contract_id.id, 'name': u'Heures majorées jour férié'}
        ]

        worked_days_lines = self.worked_days_line_ids.browse([])
        for worked_days_data in worked_days_data_list:
            self.worked_days_line_ids += worked_days_lines.new(worked_days_data)

        date_from = datetime.strptime(self.date_from, DEFAULT_SERVER_DATE_FORMAT).month
        input_data_list = [
            # {'code': 'AVANCE15', 'contract_id': self.contract_id.id, 'amount': self.get_avance_salaire(), 'name': 'Avance quinzaine'},
            {'code': 'AVANCE15', 'contract_id': self.contract_id.id, 'name': 'Avance sur salaire'},
            {'code': 'AVANCESP', 'contract_id': self.contract_id.id, 'name': u'Avance spécial'},
            {'code': 'PRM', 'contract_id': self.contract_id.id, 'name': 'Prime'},
            {'code': 'AUTRES', 'contract_id': self.contract_id.id, 'name': 'Autres retenues'},
        ]
        thirteen_month = self.env.ref('gestion_de_paie.hr_rule_basic_TM')
        if date_from == 12:
            thirteen_month.write({'active': True})
            input_data_list.append({'code': 'TM', 'contract_id': self.contract_id.id, 'name': u'Treizième mois'})
        else:
            thirteen_month.write({'active': False})
        input_lines = self.input_line_ids.browse([])
        for input_data in input_data_list:
            self.input_line_ids += input_lines.new(input_data)

        #    set average_gross
        # self.average_gross = self.get_average_gross()
        # self.average_gross_notice = self.get_average_gross_notice()
        # self.rest_leave = self._rest_leave()
        return

    etat_salaire_id = fields.Many2one('etat.salaire', string='Etat salaire')
    ostie_id = fields.Many2one('ostie', string='Etat OSTIE')
    irsa_id = fields.Many2one('irsa', string='Etat IRSA')
    cnaps_id = fields.Many2one('cnaps', string='Etat CNAPS')

    @api.model
    def create(self, vals):
        payslip_id = super(HrPayslip, self).create(vals)

        payslip_obj = self.env['hr.payslip']
        data = payslip_obj.browse([payslip_id.id])
        vals = {
            'employee_id': data.employee_id.id,
            'num_emp': data.employee_id.num_emp,
            'num_cin': data.employee_id.num_cin,
            'name_related': data.employee_id.name,
            'date_from': data.date_from,
            'date_to': data.date_to,
        }
        data_ostie = {
            'employee_id': data.employee_id.id,
            'num_emp': data.employee_id.num_emp,
            'name_related': data.employee_id.name,
            'date_from': data.date_from,
            'date_to': data.date_to,
            'omsi': '',
            'omsiemp': '',
            'brut': '',
            'net': '',
        }

        etat_id = self.env['etat.salaire'].create(vals).id
        # ostie_id = self.env['ostie'].create(vals).id
        irsa_id = self.env['irsa'].create(vals).id
        cnaps_id = self.env['cnaps'].create(vals).id

        payslip_obj.browse(payslip_id.id).write({
            'etat_salaire_id': etat_id,
            # 'ostie_id': ostie_id,
            'irsa_id': irsa_id,
            'cnaps_id': cnaps_id
        })
        return payslip_id

    @api.multi
    def write(self, values):
        result = super(HrPayslip, self).write(values)
        data = self.browse(self.id)
        if not (data.etat_salaire_id and data.cnaps_id and data.irsa_id):
            return result
        vals = {
            'employee_id': data.employee_id.id,
            'num_emp': data.employee_id.num_emp,
            'num_cin': data.employee_id.num_cin,
            # 'name_related': data.employee_id.name,
            'date_from': data.date_from,
            'date_to': data.date_to,
            'hs': 0.0,
        }
        for line in data.line_ids:
            if line.code == 'BASIC':
                vals['basic'] = line.total
            if line.code == 'OMSI_EMP':
                vals['omsi'] = line.total
            if line.code == 'CNAPS_EMP':
                vals['cnaps'] = line.total
            if line.code == 'GROSS':
                vals['brut'] = line.total
            if line.code == 'IRSA':
                vals['irsa'] = line.total

            # for line in data.details_by_salary_rule_category:
            if line.code == 'OSTIE_PAT':
                vals['omsiemp'] = line.total
            if line.code == 'CNAPS_PAT':
                vals['cnapsemp'] = line.total
            if line.code == 'NET':
                vals['net'] = line.total
            # just use the logic of the code
            if line.code == 'PRM':
                vals['prm'] = line.total
            if line.code in set(['HS1', 'HS2', 'HMNUIT', 'HMDIM', 'HMDIM', 'HMJF']):
                vals['hs'] += line.total
            # TODO ask Eric
            # if line.code == '':
            #     vals['retenus'] = line.total
            if line.code == 'AF':
                vals['af'] = line.total
            if line.code == 'CHARGE_PAT':
                vals['charge_pat'] = line.total


        vals['totalomsi'] = vals.get('omsi', 0.0) + vals.get('omsiemp', 0.0)
        vals['totalcnaps'] = vals.get('cnaps', 0.0) + vals.get('cnapsemp', 0.0)
        # etat_salaire
        etat = self.env['etat.salaire'].browse(data.etat_salaire_id.id)
        etat.write(vals)

        # Todo : change field to computed one
        # ostie object
        # vals_ostie = vals.copy()
        # not_in_ostie = ['totalcnaps']
        # not_in_ostie = set(not_in_ostie)
        # for cle in not_in_ostie:
        #     if cle in vals_ostie:
        #         del vals_ostie[cle]
        #
        # ostie = self.env['ostie'].browse(data.ostie_id.id)
        # ostie.write(vals_ostie)

        # irsa
        vals_irsa = vals.copy()
        not_in_irsa = ['cnaps', 'cnapsemp', 'totalcnaps', 'omsi', 'omsiemp', 'totalomsi', 'prm', 'hs', 'retenus', 'af', 'CHARGE_PAT']
        for cle in not_in_irsa:
            if cle in vals_irsa:
                del vals_irsa[cle]
        irsa = self.env['irsa'].browse(data.irsa_id.id)
        irsa.write(vals_irsa)

        # cnaps
        vals_cnaps = vals.copy()
        not_in_cnaps = ['irsa', 'omsi', 'omsiemp', 'totalomsi', 'prm', 'hs', 'retenus', 'af', 'CHARGE_PAT']
        for cle in not_in_cnaps:
            if cle in vals_cnaps:
                del vals_cnaps[cle]
        cnaps = self.env['cnaps'].browse(data.cnaps_id.id)
        cnaps.write(vals_cnaps)
        return result

    @api.multi
    def print_payroll(self):
        self.appears_on_calcul()
        return self.env['report'].get_action(self, 'gestion_de_paie.report_paie')

    # =========================================================================================
    @api.model
    def get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            if category.code in localdict['categories'].dict:
                amount += localdict['categories'].dict[category.code]
            localdict['categories'].dict[category.code] = amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(amount) as sum
                        FROM hr_payslip as hp, hr_payslip_input as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                        FROM hr_payslip as hp, hr_payslip_worked_days as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                                FROM hr_payslip as hp, hr_payslip_line as pl
                                WHERE hp.employee_id = %s AND hp.state = 'done'
                                AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs}
        # get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        structure_ids = contracts.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule.satisfy_condition(localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule.compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return [value for code, value in result_dict.items()]

    @api.one
    @api.depends('stc', 'additional_gross')
    def _compute_average_gross(self):
        self.ensure_one()
        if self.stc:
            base_seniority = 12
            match_seniority = self.seniority.split()
            # ilay année n atao * 12
            total_seniority = int(match_seniority[0]) * 12 + int(match_seniority[2])
            limit = 12
            if total_seniority < 12:
                base_seniority = total_seniority if total_seniority else 1  # avoid dividing by 0
            # if the hr.payslip is already in db
            if not isinstance(self.id, models.NewId):
                domain = [('employee_id', '=', self.employee_id.id), ('date_from', '<=', self.date_from), ('id', '!=', self.id)]
            else:
                domain = [('employee_id', '=', self.employee_id.id), ('date_from', '<=', self.date_from)]
            # could be self.env.cr.execute() but ...
            sum_sbr = sum(self.search(domain, order='create_date desc', limit=limit).mapped('line_ids').filtered(lambda x: x.code == 'GROSS').mapped('amount'))
            # sum_average_gross = sum(self.search(domain, order='create_date desc', limit=limit).mapped('average_gross'))
            self.average_gross = round((sum_sbr + self.additional_gross) / base_seniority, 2)

    @api.one
    @api.depends('stc', 'preavis')
    def _compute_average_gross_prv(self):
        self.ensure_one()
        if self.stc and self.priornotice:
            match_seniority = self.seniority.split()
            total_seniority = int(match_seniority[0]) * 12 + int(match_seniority[2])
            base_seniority = total_seniority if total_seniority else 1  # avoid dividing by 0
            limit = 2
            if not isinstance(self.id, models.NewId):
                domain = [('employee_id', '=', self.employee_id.id), ('date_from', '<=', self.date_from), ('id', '!=', self.id)]
            else:
                domain = [('employee_id', '=', self.employee_id.id), ('date_from', '<=', self.date_from)]
            sum_sbr = sum(self.search(domain, order='create_date desc', limit=limit).mapped('line_ids').filtered(lambda x: x.code == 'GROSS').mapped('amount'))
            self.average_gross_notice = round((sum_sbr + self.additional_gross) / base_seniority, 2)

    # TODO make call with supper in begining
    @api.multi
    def compute_sheet(self):
        for payslip in self:
            payslip.appears_on_calcul()
            number = payslip.number or payslip.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                           payslip.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in payslip.get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
            payslip.average_gross = payslip.get_average_gross_funct()
            payslip.average_gross_notice = payslip.get_average_gross_notice_funct()
            payslip.preavis = payslip.get_preavis()
            # TODO make ORM friendly not those two instruction
            # ostie_id = payslip.env['ostie'].create({'payslip_id': payslip.id})
            # payslip.ostie_id = ostie_id.id
        # return True

    @api.multi
    def appears_on_calcul(self):
        for payslip in self:
            activated_paid_leave = payslip.env.ref('gestion_de_paie.hr_holiday_rest')
            activated_paid_preavis = payslip.env.ref('gestion_de_paie.hr_payroll_rules_preavis')
            stc_ = payslip.env['hr.payslip'].search(
                [('stc', '=', payslip.stc), ('employee_id', '=', payslip.employee_id.id),
                 ('date_from', '=', payslip.date_from)], limit=1).mapped('stc')
            if stc_[0] or payslip.stc or payslip.rest_leave != 0:
                appears = True
            else:
                appears = False

            activated_paid_leave.write({'active': appears})
            activated_paid_leave.write({'appears_on_payslip': appears})
            activated_paid_preavis.write({'active': appears})
            activated_paid_preavis.write({'appears_on_payslip': appears})

            if payslip.priornotice == 0 or appears is False:
                activated_paid_preavis.write({'active': False})
                activated_paid_preavis.write({'appears_on_payslip': False})
            else:
                activated_paid_preavis.write({'active': True})
                activated_paid_preavis.write({'appears_on_payslip': True})
            if payslip.rest_leave == 0 or appears is False:
                activated_paid_leave.write({'appears_on_payslip': False})
                activated_paid_leave.write({'active': False})
            else:
                activated_paid_leave.write({'appears_on_payslip': True})
                activated_paid_leave.write({'active': True})

            if payslip.priornotice < 0 or appears is False:
                activated_paid_preavis.write({'sequence': 150})
            else:
                activated_paid_preavis.write({'sequence': 102})

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        if self.contract_id.custom_hour_bool:
            for d in res:
                d['number_of_hours'] = self.contract_id.number_of_hours
        return res

    @api.one
    @api.depends("contract_id.date_start", "date_to")
    def _compute_seniority(self):
        """ Compute Seniority at Date Payslip """
        date_start = fields.Date.from_string(self.contract_id.date_start)
        date_end = fields.Date.from_string(self.date_to)
        current = relativedelta(date_end, date_start)
        print current
        years = "0 année(s)" if not current.years else str(current.years) + " année(s)"
        months = "0 mois" if not current.months else str(current.months) + " mois"
        days = " 0 Jour" if not current.days else str(current.days) + " jour(s)"
        self.seniority = ("%s %s %s") % (years, months, days)
    # quantité du congée

    # ===========================================================================
    # def unlink(self, cr, uid, ids, context=None):
    #     context['forcer_suppresion'] = True
    #     for data in self.browse(cr, uid, ids, context=context):
    #         self.pool.get('etat.salaire2').unlink(cr, uid, [data.etat_salaire_id.id], context=context)
    #         self.pool.get('ostie').unlink(cr, uid, [data.ostie_id.id], context=context)
    #         self.pool.get('irsa2').unlink(cr, uid, [data.irsa_id.id], context=context)
    #         self.pool.get('cnaps2').unlink(cr, uid, [data.cnaps_id.id], context=context)
    #     super(hr_payslip, self).unlink(cr, uid, ids, context=context)
# ===========================================================================

    # new method for computing leaves
    # date and datetime format have string representation in Odoo Object. This is not the case in Odoo upper version
    def _get_leaves(self):
        domain_taken_leaves = [
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
            ('type', '=', 'remove'), ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to)
        ]
        domain_alloc_leaves = [
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('type', '=', 'add'),
            ('allocation_month', '=', fields.Datetime.from_string(self.date_from).month),
            ('allocation_year', '=', fields.Datetime.from_string(self.date_from).year)
        ]
        last_month_date = datetime.strptime(self.date_from, '%Y-%m-%d') + relativedelta(months=-1)
        year = int(last_month_date.strftime("%Y"))
        month = int(last_month_date.strftime("%m"))
        begin_last_month_day = 1
        end_last_month_day = calendar.monthrange(year, month)[1]
        end_last_month_date = datetime.strptime('%s-%s-%s' % (year, month, end_last_month_day), '%Y-%m-%d')
        # new implementation, 3 years cumul leaves
        contract_date_start = fields.Date.from_string(self.contract_id.date_start)
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)

        current = relativedelta(date_from, contract_date_start)
        date_begin_x = contract_date_start


        # TODO : alloc leave can be optimize, use SQL
        # TODO : take to account day and month in 3 years algo
        if current.years > 3:
            # TODO take account month too
            gaps = current.years - 3
            date_begin_x = contract_date_start + relativedelta(years=gaps)
        if year == date_from.year:
            domain_alloc_anc_leaves = [
                ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('type', '=', 'add'),
                ('allocation_month', 'in', [x + 1 for x in range(12)]), ('allocation_year', 'in', [y for y in range(date_begin_x.year, date_from.year)])
            ]
            domain_alloc_anc_leaves_1 = [
                ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('type', '=', 'add'),
                ('allocation_month', 'in', [x + 1 for x in range(month)]), ('allocation_year', '=', date_from.year),
            ]
            alloc_anc_leaves = sum(self.env['hr.holidays'].search(domain_alloc_anc_leaves).mapped('number_of_days_temp')) + sum(self.env['hr.holidays'].search(domain_alloc_anc_leaves_1).mapped('number_of_days_temp'))
        else:
            domain_alloc_anc_leaves = [
                ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('type', '=', 'add'),
                ('allocation_month', 'in', [x + 1 for x in range(12)]), ('allocation_year', 'in', [y for y in range(date_begin_x.year, date_from.year)])
            ]
            alloc_anc_leaves = sum(self.env['hr.holidays'].search(domain_alloc_anc_leaves).mapped('number_of_days_temp'))

        domain_taken_entre_mois = [
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
            ('type', '=', 'remove'), ('date_from', '>=', date_begin_x.strftime("%Y-%m-%d")),
            ('date_to', '<=', self.date_to)
        ]

        domain_taken_entre_mois_1 = [
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
            ('type', '=', 'remove'), ('date_from', '>=', self.date_from),
            ('date_from', '<=', self.date_to)
        ]

        domain_taken_anc_leaves = [
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
            ('type', '=', 'remove'), ('date_from', '>=', date_begin_x.strftime("%Y-%m-%d")),
            ('date_to', '<=', end_last_month_date.strftime("%Y-%m-%d"))
        ]
        taken_anc_leaves = self.env['hr.holidays'].search(domain_taken_anc_leaves)
        taken_entre_mois = self.env['hr.holidays'].search(domain_taken_entre_mois)
        pris = self.env['hr.holidays'].search(domain_taken_leaves)
        taken_entre_mois = list(set(taken_entre_mois).difference(taken_anc_leaves))
        taken_entre_mois = list(set(taken_entre_mois).difference(pris))
        taken_entre_mois_1 = self.env['hr.holidays'].search(domain_taken_entre_mois_1)
        taken_entre_mois_1 = list(set(taken_entre_mois_1).difference(pris))
        taken_entre_mois_1 = list(set(taken_entre_mois_1).difference(taken_entre_mois))

        # calculate taken entre mois
        # this doesn't take account sunday and saturday
        # this is fucking linear O(n) n number of day
        # Can be optimise, try dichotomic style
        taken_current_month = 0
        taken_anc_month = 0
        for t in taken_entre_mois:
            temp_date_begin = fields.Date.from_string(t.date_from)
            temp_date_ending = fields.Date.from_string(t.date_to)
            while temp_date_begin < date_from:
                temp_date_begin = temp_date_begin + timedelta(days=1)
                if temp_date_begin.strftime("%w") == '0' or temp_date_begin.strftime("%w") == '1':
                    continue
                taken_anc_month += 1
            while temp_date_ending >= date_from:
                temp_date_ending = temp_date_ending - timedelta(days=1)
                if temp_date_ending.strftime("%w") == '0' or temp_date_ending.strftime("%w") == '1':
                    continue
                taken_current_month += 1

        taken_current_month_1 = 0
        for t in taken_entre_mois_1:
            temp_date_begin = fields.Date.from_string(t.date_from)
            while temp_date_begin <= date_to:
                temp_date_begin = temp_date_begin + timedelta(days=1)
                if temp_date_begin.strftime("%w") == '0' or temp_date_begin.strftime("%w") == '1':
                    continue
                taken_current_month_1 += 1

        acquis = sum(self.env['hr.holidays'].search(domain_alloc_leaves).mapped('number_of_days_temp'))
        sum_pris = sum(pris.mapped('number_of_days_temp')) + taken_current_month + taken_current_month_1
        anc = alloc_anc_leaves - sum(taken_anc_leaves.mapped('number_of_days_temp')) - taken_anc_month
        solde = acquis - sum_pris + anc

        # or send immutable object
        leaves = {
            'anc': anc,
            'acquis': acquis,
            'pris': sum_pris,
            'solde': solde,
        }

        return leaves

    @api.multi
    def action_payslip_done(self):
        ret = super(HrPayslip, self).action_payslip_done()
        ostie_id = self.env['ostie'].create({'payslip_id': self.id})
        self.ostie_id = ostie_id.id
        return ret
