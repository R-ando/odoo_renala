# -*- coding:utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    categorie = fields.Char('Categorie Professionnel', size=64)
    echellon = fields.Char('Echellon', size=64)
    indice = fields.Integer('Indice', size=10)
    horaire_hebdo = fields.Float('Horaire hebdomadaire')
    payment_mode_id = fields.Many2one(string="Mode de paiement", comodel_name="hr.payment.mode")


class res_company(models.Model):
    _inherit = 'res.company'

    seuil_irsa = fields.Float('Seuil IRSA')
    taux_irsa = fields.Float('Taux IRSA')
    abat_irsa = fields.Float('Abattement IRSA')
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
    seuil_fmfp = fields.Float('FMFP')


res_company()


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    num_cnaps_emp = fields.Char(u'Numéro CNAPS', size=64)
    num_emp = fields.Char(u'Numéro Matricule', size=64)
    num_cin = fields.Char(u'Numéro CIN', size=64)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    paiement_mode_id = fields.Many2one(related='contract_id.payment_mode_id')
    stc = fields.Boolean(string='STC')
    half_salary = fields.Boolean(string='Demi salaire')
    rest_leave = fields.Integer(compute='_rest_leave', string=u"Congé payé")
    priornotice = fields.Integer(string=u"Préavis", store=True)
    average_gross = fields.Float(compute='get_average_gross', inverse='set_average_gross', string=u"SBR Moyen", store=True)
    average_gross_notice = fields.Float(compute='get_average_gross', inverse='set_average_gross_notice', string=u"SBR moyen préavis", store=True)

    @api.multi
    @api.onchange('employee_id', 'date_from')
    def _rest_leave(self):
        activated_paid_leave = self.env.ref('gestion_de_paie.hr_holiday_rest')
        activated_paid_leave.write({'active': True})
        conge_pris = self._get_employee_request_leaves(self.employee_id, self.date_from, self.date_to, True)
        conge_attr = self._get_employee_allocation_leaves(self.employee_id, self.date_from)
        self.rest_leave = conge_attr - conge_pris

    def set_average_gross(self):
        for payslip in self:
            payslip.average_gross = float(payslip.average_gross) if payslip.average_gross else False

    def set_average_gross_notice(self):
        for payslip in self:
            payslip.average_gross_notice = float(payslip.average_gross_notice) if payslip.average_gross_notice else False

    # tokon atao date start ian leiz a
    @api.multi
    @api.onchange('employee_id', 'date_from')
    def get_average_gross(self):
        if self.employee_id:
            date_start = \
            self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)]).mapped('date_start')[0].split(
                '-')
            date_from = self.date_from.split('-')
            seniority = self.diff_month(datetime(int(date_from[0]), int(date_from[1]), int(date_from[2])),
                                        datetime(int(date_start[0]), int(date_start[1]), int(date_start[2])))
            payslip_obj = self.search([('state', '=', 'done')])
            hr_payslip_line_obj = self.env['hr.payslip.line']
            sum_gross_done = 0.0

            if seniority < 12 and seniority != 0:
                for line in payslip_obj:
                    sum_gross_done += hr_payslip_line_obj.search([('slip_id', '=', line.id), ('code', '=', 'GROSS')]).mapped('amount')[0]
                self.average_gross = sum_gross_done / seniority
                sum_gross_done_medium = 0.0
                if seniority > 2:
                    query = """ SELECT id from hr_payslip where employee_id = '{}' order by date_from desc limit 2 """.format(
                        self.employee_id.id)
                    self.env.cr.execute(query)
                    two_payslip_id = self.env.cr.dictfetchall()
                    for payslip_id in two_payslip_id:
                        sum_gross_done_medium += hr_payslip_line_obj.search(
                            [('slip_id', '=', payslip_id['id']), ('code', '=', 'GROSS')]).mapped('amount')[0]
                    self.average_gross_notice = sum_gross_done_medium / seniority
                else:
                    self.average_gross_notice = sum_gross_done / seniority
            else:
                last_year = int(self.date_from.split('-')[0]) - 1
                payslip_obj_last_year = self.search(
                    [('employee_id', '=', self.employee_id.id), ('date_from', 'like', str(last_year) + '%')])
                for line in payslip_obj_last_year:
                    sum_gross_done += \
                    hr_payslip_line_obj.search([('slip_id', '=', line.id), ('code', '=', 'GROSS')]).mapped('amount')[0]
                self.average_gross = sum_gross_done / 12

    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

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

    def prior_notice(self):
        pass

    def get_avance_salaire(self):
        advance_obj = self.env['hr.wage.advance']
        advances = advance_obj.search(['&', '&', '&', ('employee_id', '=', self.employee_id.id), ('state', '=', 'ok'),
                                       ('date', '>=', self.date_from), ('date', '<=', self.date_to)])
        total_advance = 0.0
        for advance in advances:
            total_advance += advance.amount
        return total_advance

    # Redefinition fonction onchange_employee()

    @api.onchange('employee_id', 'date_from')
    def onchange_employee(self):
        res = super(HrPayslip, self).onchange_employee()

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        worked_days_data_list = [
            {'code': 'HS1', 'contract_id': self.contract_id.id, 'name': u'Heure supplémentaire 1'},
            {'code': 'HS2', 'contract_id': self.contract_id.id, 'name': u'Heure supplémentaire 2'},
            {'code': 'HMNUIT', 'contract_id': self.contract_id.id, 'name': u'Heure majoré nuit'},
            {'code': 'HMDIM', 'contract_id': self.contract_id.id, 'name': u'Heure majoré dimanche'},
            {'code': 'HMJF', 'contract_id': self.contract_id.id, 'name': u'Heure majoré jour férié'}
        ]

        worked_days_lines = self.worked_days_line_ids.browse([])
        for worked_days_data in worked_days_data_list:
            self.worked_days_line_ids += worked_days_lines.new(worked_days_data)

        date_from = datetime.strptime(self.date_from, DEFAULT_SERVER_DATE_FORMAT).month
        input_data_list = [
            # {'code': 'AVANCE15', 'contract_id': self.contract_id.id, 'amount': self.get_avance_salaire(), 'name': 'Avance quinzaine'},
            {'code': 'AVANCE15', 'contract_id': self.contract_id.id, 'name': 'Avance quinzaine'},
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
        etat_id = self.env['etat.salaire'].create(vals).id
        ostie_id = self.env['ostie'].create(vals).id
        irsa_id = self.env['irsa'].create(vals).id
        cnaps_id = self.env['cnaps'].create(vals).id

        payslip_obj.browse(payslip_id.id).write({
            'etat_salaire_id': etat_id,
            'ostie_id': ostie_id,
            'irsa_id': irsa_id,
            'cnaps_id': cnaps_id
        })
        return payslip_id

    @api.multi
    def write(self, values):
        result = super(HrPayslip, self).write(values)
        data = self.browse(self.id)
        if not (data.etat_salaire_id and data.ostie_id and data.cnaps_id and data.irsa_id):
            return result
        vals = {
            'employee_id': data.employee_id.id,
            'num_emp': data.employee_id.num_emp,
            'num_cin': data.employee_id.num_cin,
            'name_related': data.employee_id.name,
            'date_from': data.date_from,
            'date_to': data.date_to,
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
            if line.code == 'OMSI_PAT':
                vals['omsiemp'] = line.total
            if line.code == 'CNAPS_PAT':
                vals['cnapsemp'] = line.total
            if line.code == 'NET':
                vals['net'] = line.total

        vals['totalomsi'] = vals.get('omsi', 0.0) + vals.get('omsiemp', 0.0)
        vals['totalcnaps'] = vals.get('cnaps', 0.0) + vals.get('cnapsemp', 0.0)
        # etat_salaire
        etat = self.env['etat.salaire'].browse(data.etat_salaire_id.id)
        etat.write(vals)

        # ostie
        vals_ostie = vals.copy()
        not_in_ostie = ['cnaps', 'cnapsemp', 'totalcnaps', 'irsa']
        for cle in not_in_ostie:
            if cle in vals_ostie:
                del vals_ostie[cle]

        ostie = self.env['ostie'].browse(data.ostie_id.id)
        ostie.write(vals_ostie)

        # irsa
        vals_irsa = vals.copy()
        not_in_irsa = ['cnaps', 'cnapsemp', 'totalcnaps', 'omsi', 'omsiemp', 'totalomsi']
        for cle in not_in_irsa:
            if cle in vals_irsa:
                del vals_irsa[cle]
        irsa = self.env['irsa'].browse(data.irsa_id.id)
        irsa.write(vals_irsa)

        # cnaps
        vals_cnaps = vals.copy()
        not_in_cnaps = ['irsa', 'omsi', 'omsiemp', 'totalomsi']
        for cle in not_in_cnaps:
            if cle in vals_cnaps:
                del vals_cnaps[cle]
        cnaps = self.env['cnaps'].browse(data.cnaps_id.id)
        cnaps.write(vals_cnaps)

        return result

    @api.multi
    def print_payroll(self):
        return self.env['report'].get_action(self, 'gestion_de_paie.report_paie')

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
