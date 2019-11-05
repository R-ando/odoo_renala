from odoo import models, api


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.model
    def default_get(self, field_list):
        vals = super(ResourceCalendar, self).default_get(field_list)
        vals['attendance_ids'] = [
            (0, 0, {'name': 'lun m', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': 'lun s', 'dayofweek': '0', 'hour_from': 14, 'hour_to': 18}),
            (0, 0, {'name': 'mar m', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': 'mar s', 'dayofweek': '1', 'hour_from': 14, 'hour_to': 18}),
            (0, 0, {'name': 'mer m', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': 'mer s', 'dayofweek': '2', 'hour_from': 14, 'hour_to': 18}),
            (0, 0, {'name': 'jeu m', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': 'jeu s', 'dayofweek': '3', 'hour_from': 14, 'hour_to': 18}),
            (0, 0, {'name': 'ven m', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12}),
            (0, 0, {'name': 'ven s', 'dayofweek': '4', 'hour_from': 14, 'hour_to': 18})
        ]
        return vals
