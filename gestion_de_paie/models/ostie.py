# -*- coding: utf-8 -*-

import datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.http import request

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
    total_cnaps = fields.Float('TOTAL CNaPS')
    prm = fields.Float(string='Prime')
    hs = fields.Float(string='Heures supp')
    retenus = fields.Float(string='Retenues')
    irsa = fields.Float(string="IRSA")
    employee_id = fields.Many2one(comodel_name='hr.employee')
    num_cnaps_emp = fields.Char(string=u'N° CNaPS', related='employee_id.num_cnaps_emp', size=64)
    af = fields.Float(string="Allocation F.")
    charge_pat = fields.Float(string="Charge employeur")

    @api.multi
    def generate_report(self):
        if len(self.ids) == 1:
            return self.env["report"].with_context(active_ids=self.ids, active_model='ostie').get_action([], 'gestion_de_paie.report_ostie')
        else:
            actions = {
                # 'type': 'ir.actions.act_url',
                # 'target': 'current',
                # 'url': '/web/binary/',
            }
            return actions

    # ===========================================================================
    # def unlink(self, cr, uid, ids, context=None):
    #     context = context or {}
    #     if not context.get('forcer_suppresion'):
    #         raise ValidationError( 'Supprimer le bulletin de paie lié pour une suppression')
    #
    #     super(ostie, self).unlink(cr, uid, ids, context=context)
    # ===========================================================================
