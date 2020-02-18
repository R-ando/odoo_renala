# -*- coding: utf-8 -*-
# Copyright 2019, Boris FITIAVAMAMONJY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import io
import xlsxwriter
from ast import literal_eval
from datetime import datetime

from odoo import http
from odoo.http import content_disposition, request

import logging

logger = logging.getLogger(__name__)


class ExportGeneralState(http.Controller):
    """Function to export New Product Excel """

    @http.route('/web/binary/general_state', type='http', auth="public")
    def download_general_state(self, context, **args):
        filename = "General state.xlsx"

        active_ids = eval(context)
        ostie = request.env['ostie'].sudo().browse(active_ids)

        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()

        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("New Product")

        # Add a numbformat for cells with money.
        titre_format = workbook.add_format({'align': "center", "bg_color": "#ffa500", "font_color": "white"})
        money_format = workbook.add_format({'num_format': '# ### ##0 [$MGA]'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        row = 0
        worksheet.write(row, 0, "Matricule", titre_format)
        worksheet.write(row, 1, "Nom", titre_format)
        worksheet.write(row, 2, "CIN", titre_format)
        worksheet.write(row, 3, "Sal. Base", titre_format)
        worksheet.write(row, 4, "Prime", titre_format)
        worksheet.write(row, 5, "Heure Suppl", titre_format)
        worksheet.write(row, 6, "Retenues", titre_format)
        worksheet.write(row, 7, "Sal. Brut", titre_format)
        worksheet.write(row, 8, "Brut plafonné", titre_format)
        worksheet.write(row, 9, "OSTIE Travailleur 1%", titre_format)
        worksheet.write(row, 10, "OSTIE Employeur 5%", titre_format)
        worksheet.write(row, 11, "Total Ostie")
        worksheet.write(row, 12, "N° CnaPS")
        worksheet.write(row, 13, "Allocation F.")
        worksheet.write(row, 14, "Nbre de charge")
        worksheet.write(row, 15, "CNAPS Travailleur 1%")
        worksheet.write(row, 16, "CNAPS Employeur 13%")
        worksheet.write(row, 17, "Total CNAPS")
        worksheet.write(row, 18, "IRSA")
        worksheet.write(row, 19, "Sal. Net")
        worksheet.write(row, 20, "CHARGE Employeur")
        worksheet.write(row, 21, "Période")

        row += 1

        logger.debug("Ostie: {}".format(ostie))

        for o in ostie:
            worksheet.write(row, 0, 0)
            worksheet.write(row, 1, 0)
            worksheet.write(row, 2, 0)
            worksheet.write(row, 3,0, money_format)
            worksheet.write(row, 4, 0)
            worksheet.write(row, 5, 0, date_format)
            worksheet.write(row, 6, 0, date_format)
            worksheet.write(row, 7, 0)
            worksheet.write(row, 8, 0)
            worksheet.write(row, 9, 0, money_format)
            worksheet.write(row, 10, 0)
            worksheet.write(row, 11, 0)
            worksheet.write(row, 12, 0)
            worksheet.write(row, 13, 0)
            worksheet.write(row, 14, 0)
            worksheet.write(row, 15, 0)
            worksheet.write(row, 16, 0)
            worksheet.write(row, 17, 0)
            worksheet.write(row, 18, 0)
            worksheet.write(row, 19, 0)
            row += 1

        workbook.close()

        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', content_disposition(filename))]
        return request.make_response(output, xlsheader)

