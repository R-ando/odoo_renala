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
        worksheet.write(row, 0, u"Matricule", titre_format)
        worksheet.write(row, 1, u"Nom", titre_format)
        worksheet.write(row, 2, u"CIN", titre_format)
        worksheet.write(row, 3, u"Sal. Base", titre_format)
        worksheet.write(row, 4, u"Prime", titre_format)
        worksheet.write(row, 5, u"Heure Suppl", titre_format)
        worksheet.write(row, 6, u"Retenues", titre_format)
        worksheet.write(row, 7, u"Sal. Brut", titre_format)
        worksheet.write(row, 8, u"Brut plafonné", titre_format)
        worksheet.write(row, 9, u"OSTIE Travailleur 1%", titre_format)
        worksheet.write(row, 10, u"OSTIE Employeur 5%", titre_format)
        worksheet.write(row, 11, u"Total Ostie", titre_format)
        worksheet.write(row, 12, u"N° CnaPS", titre_format)
        worksheet.write(row, 13, u"Allocation F.", titre_format)
        worksheet.write(row, 14, u"Nbre de charge", titre_format)
        worksheet.write(row, 15, u"CNAPS Travailleur 1%", titre_format)
        worksheet.write(row, 16, u"CNAPS Employeur 13%", titre_format)
        worksheet.write(row, 17, u"Total CNAPS", titre_format)
        worksheet.write(row, 18, u"IRSA", titre_format)
        worksheet.write(row, 19, u"Sal. Net", titre_format)
        worksheet.write(row, 20, u"CHARGE Employeur", titre_format)
        worksheet.write(row, 21, u"Période", titre_format)

        row += 1

        logger.debug("Ostie: {}".format(ostie))

        for o in ostie:
            worksheet.write(row, 0, o.employee_id.num_emp)
            worksheet.write(row, 1, o.employee_id.name)
            worksheet.write(row, 2, o.num_cin)
            worksheet.write(row, 3, o.basic)
            worksheet.write(row, 4, o.prm)
            worksheet.write(row, 5, o.hs)
            worksheet.write(row, 6, o.retenus)
            worksheet.write(row, 7, o.brut)
            worksheet.write(row, 8, o.brut_plafon)
            worksheet.write(row, 9, o.omsi, money_format)
            worksheet.write(row, 10, o.omsiemp)
            worksheet.write(row, 11, o.totalomsi)
            worksheet.write(row, 12, o.num_cnaps_emp)
            worksheet.write(row, 13, o.af)
            worksheet.write(row, 14, o.nbr_charge)
            worksheet.write(row, 15, o.cnaps)
            worksheet.write(row, 16, o.cnapsemp)
            worksheet.write(row, 17, o.total_cnaps)
            worksheet.write(row, 18, o.irsa)
            worksheet.write(row, 19, o.net)
            worksheet.write(row, 20, o.charge_pat)

            date = o.date_from + " " + o.date_to
            worksheet.write(row, 21, date)
            row += 1

        workbook.close()

        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', content_disposition(filename))]
        return request.make_response(output, xlsheader)

