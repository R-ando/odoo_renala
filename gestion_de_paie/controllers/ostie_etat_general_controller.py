# -*- coding: utf-8 -*-

import io

import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request


class OstieEtatGeneral(http.request):
    filename = "etat_general.xlsx"
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    @http.route('/web/binary/download_report_etat_general', type='http', auth='public')
    def generate_xls(self):
        self.workbook.close()
        self.output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % self.filename)]
        return request.make_response(self.output, xlsheader)
