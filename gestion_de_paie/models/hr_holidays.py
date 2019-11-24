# -*- coding: utf-8 -*-

from odoo import fields, models
from datetime import datetime

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'


    def _get_current_month(self):
        return str(datetime.today().month)

    def _get_current_year(self):
        return datetime.today().year

    allocation_month = fields.Selection(
        [('1', 'Janvier'),
         ('2', u'Février'),
         ('3', 'Mars'),
         ('4', 'Avril'),
         ('5', 'Mai'),
         ('6', 'Juin'),
         ('7', 'Juillet'),
         ('8', u'Août'),
         ('9', 'Septembre'),
         ('10', 'Octobre'),
         ('11', 'Novembre'),
         ('12', u'Décembre')],
        string="Mois d'attribution",
        default=_get_current_month,
    )
    allocation_year = fields.Integer(
        string="Année d'attribution",
        default=_get_current_year,
    )

    def get_total_leave(self):
        return
