# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools.translate import _


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    @api.multi
    def name_get(self):
        if not self._context.get('employee_id'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(HolidaysType, self).name_get()
        res = []
        for record in self:
            name = record.name
            name = "%(name)s (%(count)s)" % {
                'name': name,
                'count': _('%g remaining out of %g') % (record.virtual_remaining_leaves or 0.0, record.max_leaves or 0.0)
            }
            res.append((record.id, name))
        return res
