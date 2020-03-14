# -*- coding: utf-8 -*-

import datetime

from odoo import fields, models, api

# TODO make related field and compute field instead
# TODO rename model

class ostie(models.Model):
    _name = "ostie"
    _description = u"Etat général"

    payslip_id = fields.Many2one('hr.payslip', string=u'Employé')
    num_emp = fields.Char('Matricule', size=128)
    num_cin = fields.Char('CIN', size=128)
    name_related = fields.Char('Nom', size=128, related="payslip_id.employee_id.name")
    basic = fields.Float('Salaire de base', compute="_compute_basic")
    omsi = fields.Float('OSTIE Travailleur', compute="_compute_omsi")
    omsiemp = fields.Float('OSTIE Employeur', compute="_compute_omsiemp")
    cnaps = fields.Float("CNAPS Travailleur", compute="_compute_cnaps")
    cnapsemp = fields.Float("CNAPS Employeur", compute="_compute_cnapsemp")
    brut = fields.Float('Salaire Brut', compute="_compute_brut")
    net = fields.Float('Salaire Net', compute="_compute_net")
    date_from = fields.Date('Start Date', related="payslip_id.date_from")
    date_to = fields.Date('End Date', related="payslip_id.date_to")
    totalomsi = fields.Float('TOTAL OSTIE', compute="_compute_total_omsi")
    avantage = fields.Float('Avantage du mois', compute="_compute_avantage")
    temps_presence = fields.Float('Temps presence', compute="_compute_temps_presence")
    # new fields
    total_cnaps = fields.Float('TOTAL CNaPS', compute="_total_cnaps")
    prm = fields.Float(string='Prime', compute="_compute_prm")
    hs = fields.Float(string='Heures supp', compute="_compute_hs")
    retenus = fields.Float(string='Retenues', compute="_compute_retenus")
    irsa = fields.Float(string="IRSA", compute="_compute_irsa")
    employee_id = fields.Many2one(comodel_name='hr.employee', related="payslip_id.employee_id", store=True)
    num_cnaps_emp = fields.Char(string=u'N° CNaPS', related='employee_id.num_cnaps_emp', size=64)
    af = fields.Float(string="Allocation F.", compute="_compute_allocation")
    charge_pat = fields.Float(string="Charge employeur", compute="_compute_pat")
    brut_plafon = fields.Float(string=u"Brut plafonné", related="employee_id.company_id.plafond_cnaps")
    nbr_charge = fields.Integer(string=u"Nbre de charge", related="employee_id.nombre_enfant_cnaps")
    period = fields.Char(string=u"Période", compute="_get_month", size=15)
    period_s = fields.Char(string=u"Période", compute="_get_num_month", size=15, store=True)

    @api.multi
    def generate_report(self):
        if len(self.ids) == 1:
            return self.env["report"].with_context(active_ids=self.ids, active_model='ostie').get_action([], 'gestion_de_paie.report_ostie')
        else:
            ctx = self._context
            actions = {
                'type': 'ir.actions.act_url',
                'target': 'current',
                'url': '/web/binary/general_state?context={}'.format(ctx.get('active_ids'))
            }
            return actions

    @api.multi
    @api.depends('cnaps', 'cnapsemp')
    def _total_cnaps(self):
        for ostie in self:
            ostie.total_cnaps = ostie.cnaps + ostie.cnapsemp

    @api.multi
    def _compute_total_omsi(self):
        for ostie in self:
            ostie.totalomsi = ostie.omsi + ostie.omsiemp

    @api.multi
    @api.depends('date_from')
    def _get_month(self):
        for ostie in self:
            ostie.period = datetime.datetime.strptime(ostie.date_from, "%Y-%m-%d").strftime("%B").upper() if ostie.date_from else False

    @api.multi
    @api.depends('date_from')
    def _get_num_month(self):
        for ostie in self:
            ostie.period_s = datetime.datetime.strptime(ostie.date_from, "%Y-%m-%d").strftime("%m %B").upper() if ostie.date_from else False

    @api.multi
    def _compute_basic(self):
        for ostie in self:
            ostie.basic = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'BASIC').mapped('total'))

    @api.multi
    def _compute_omsi(self):
        for ostie in self:
            ostie.omsi = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'OMSI_EMP').mapped('total'))

    @api.multi
    def _compute_omsiemp(self):
        for ostie in self:
            ostie.omsiemp = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'OMSI_PAT').mapped('total'))

    @api.multi
    def _compute_cnaps(self):
        for ostie in self:
            ostie.cnaps = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'CNAPS_EMP').mapped('total'))

    @api.multi
    def _compute_cnapsemp(self):
        for ostie in self:
            ostie.cnapsemp = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'CNAPS_PAT').mapped('total'))

    @api.multi
    def _compute_brut(self):
        for ostie in self:
            ostie.brut = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'GROSS').mapped('total'))

    @api.multi
    def _compute_net(self):
        for ostie in self:
            ostie.net = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'NET').mapped('total'))

    @api.multi
    def _compute_avantage(self):
        for ostie in self:
            ostie.avantage = 0.0

    @api.multi
    def _compute_temps_presence(self):
        for ostie in self:
            ostie.temps_presence = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'BASIC').mapped('quantity'))

    @api.multi
    def _compute_prm(self):
        for ostie in self:
            ostie.prm = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'PRM').mapped('total'))

    @api.multi
    def _compute_hs(self):
        for ostie in self:
            ostie.hs = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code in ('HS1', 'HS2', 'HMNUIT', 'HMDIM', 'HMDIM', 'HMJF')).mapped('total'))

    @api.multi
    def _compute_retenus(self):
        for ostie in self:
            ostie.retenus = 0

    @api.multi
    def _compute_irsa(self):
        for ostie in self:
            ostie.irsa = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'IRSA').mapped('total'))

    @api.multi
    def _compute_allocation(self):
        for ostie in self:
            ostie.af = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'AF').mapped('total'))

    @api.multi
    def _compute_pat(self):
        for ostie in self:
            ostie.charge_pat = sum(ostie.payslip_id.line_ids.filtered(lambda x: x.code == 'CHARGE_PAT').mapped('total'))
