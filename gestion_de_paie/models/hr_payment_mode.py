# -*- coding: utf-8 -*-

from odoo import models, fields


class Payment_mode(models.Model):
    _name = "hr.payment.mode"
    name = fields.Char(string="Mode de paiemet")




