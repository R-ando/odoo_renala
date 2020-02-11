# -*- coding: UTF-8 -*-

from odoo import models, fields
from odoo.addons import decimal_precision as dp


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    rate = fields.Float(digits=dp.get_precision('Renala Paie'))
    amount = fields.Float(digits=dp.get_precision('Renala Paie'))
    total = fields.Float(compute='_compute_total', string='Total', digits=dp.get_precision('Renala Paie'), store=True)
