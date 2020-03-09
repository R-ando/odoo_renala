# -*- coding: UTF-8 -*-

from odoo import models


# this should be in migration folder but sometime
# it migration code doesn't work so don't complicate life

class UpdateOstieModel(models.TransientModel):
    _name = 'update.ostie'

    def update_ostie(self):
        # remove all written in the ostie model
        self.env['ostie'].search([]).unlink()
        # for ostie_id in ostie_ids:
        #     ostie_id.unlik()

        ostie_obj = self.env['ostie']
        # get all 'validate' pay in hr.payslip
        payslip_ids = self.env['hr.payslip'].search([('state', '=', 'done')])
        for payslip in payslip_ids:
            ostie_id = ostie_obj.create({'payslip_id': payslip.id})
            payslip.ostie_id = ostie_id.id
