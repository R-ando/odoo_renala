# -*- coding: UTF-8 -*-

from odoo import models, api, fields


class Employee(models.Model):
    _inherit = "hr.employee"

    leaves_count = fields.Float('Number of Leaves', compute='_compute_leaves_count', digits=(14, 2))

    @api.multi
    def _compute_leaves_count(self):
        leaves = self.env['hr.holidays'].read_group([
            ('employee_id', 'in', self.ids),
            ('state', '=', 'validate')
        ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in leaves])
        for employee in self:
            employee.leaves_count = mapping.get(employee.id)
