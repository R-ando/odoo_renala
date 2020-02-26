# -*- coding: UTF-8 -*-

from odoo import models, fields
from odoo.addons import decimal_precision as dp


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _compute_total(self):
        for line in self:
            total = float(line.quantity) * line.amount * line.rate / 100
            if line.code != "HWORK":
                line.total = round(total)
            else:
                line.total = total
