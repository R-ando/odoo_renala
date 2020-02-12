# -*- coding: UTF-8 -*-

import io

import xlsxwriter

from odoo import http
from odoo.http import request


class ExportReportIrsaController(http.Controller):

    def head(self, workbook, worksheet):
        worksheet.merge_range('B1:C1', 'Nom ou raison sociale de l\'organisme payeur')
        worksheet.write(0, 3, 'profession')

    def fulfill(self, workbook, worksheet, payslips):
        self.head(workbook, worksheet)

    @http.route('/web/binary/download_report_irsa_file', type='http', auth="public")
    def generateIrsa_excel(self, year, month):
        filename = "IRSA.xlsx"
        output = io.BytesIO()
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("IRSA")

        # take periodic payslip
        payslips = request.env['hr.payslip'].search([('date_from', 'like', "%s-%s%s" % (year, month, '%'))])

        self.fulfill(workbook, worksheet, payslips)

        workbook.close()
        output.seek(0)

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % filename)]
        return request.make_response(output, xlsheader)
