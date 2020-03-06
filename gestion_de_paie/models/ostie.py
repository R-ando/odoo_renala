# -*- coding: utf-8 -*-

import datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.http import request

# TODO make related field instead

class ostie(models.Model):
    _name = "ostie"
    _description = u"Etat général"

    payslip_id = fields.Many2one('hr.payslip', string=u'Employé')
    num_emp = fields.Char('Matricule', size=128)
    num_cin = fields.Char('CIN', size=128)
    name_related = fields.Char('Nom', size=128)
    basic = fields.Float('Salaire de base')
    omsi = fields.Float('OSTIE Travailleur')
    omsiemp = fields.Float('OSTIE Employeur')
    cnaps = fields.Float("CNAPS Travailleur")
    cnapsemp = fields.Float("CNAPS Employeur")
    brut = fields.Float('Salaire Brut')
    net = fields.Float('Salaire Net')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    totalomsi = fields.Float('TOTAL OSTIE')
    avantage = fields.Float('Avantage du mois')
    temps_presence = fields.Float('Temps presence')
    # new fields
    total_cnaps = fields.Float('TOTAL CNaPS', compute="_total_cnaps")
    prm = fields.Float(string='Prime')
    hs = fields.Float(string='Heures supp')
    retenus = fields.Float(string='Retenues')
    irsa = fields.Float(string="IRSA")
    employee_id = fields.Many2one(comodel_name='hr.employee')
    num_cnaps_emp = fields.Char(string=u'N° CNaPS', related='employee_id.num_cnaps_emp', size=64)
    af = fields.Float(string="Allocation F.")
    charge_pat = fields.Float(string="Charge employeur")
    brut_plafon = fields.Float(string=u"Brut plafonné", related="employee_id.company_id.plafond_cnaps")
    nbr_charge = fields.Integer(string=u"Nbre de charge", related="employee_id.nombre_enfant_cnaps")
    period = fields.Char(string=u"Période", compute="_get_month", size=15)

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
    @api.depends('date_from')
    def _get_month(self):
        for ostie in self:
            ostie.period = datetime.datetime.strptime(ostie.date_from, "%Y-%m-%d").strftime("%B").upper()
    # ===========================================================================
    # def unlink(self, cr, uid, ids, context=None):
    #     context = context or {}
    #     if not context.get('forcer_suppresion'):
    #         raise ValidationError( 'Supprimer le bulletin de paie lié pour une suppression')
    #
    #     super(ostie, self).unlink(cr, uid, ids, context=context)
    # ===========================================================================
