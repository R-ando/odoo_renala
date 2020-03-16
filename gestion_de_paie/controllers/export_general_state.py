# -*- coding: utf-8 -*-
# Copyright 2019, Boris FITIAVAMAMONJY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import io
import logging

import xlsxwriter

from odoo import http
from odoo.http import content_disposition, request

logger = logging.getLogger(__name__)


class ExportGeneralState(http.Controller):
    # copy pasta ana boris
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
        worksheet = workbook.add_worksheet("E.G")

        # Add a format for cells.
        titre_format = workbook.add_format({'align': "center", "font_color": "black", "border": 1})
        money_format = workbook.add_format({'num_format': '# ### ##0 [$MGA]'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        border_format = workbook.add_format({'border': 1})

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

        # set column width
        worksheet.set_column('B:B', 20)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('T:T', 15)

        row += 1

        logger.debug("Ostie: {}".format(ostie))

        for o in ostie.sorted(lambda x: x.employee_id.num_emp):
            worksheet.write(row, 0, o.employee_id.num_emp if o.employee_id.num_emp else '', border_format)
            worksheet.write(row, 1, o.employee_id.name, border_format)
            worksheet.write(row, 2, o.num_cin if o.num_cin else '', border_format)
            worksheet.write(row, 3, o.basic, border_format)
            worksheet.write(row, 4, o.prm, border_format)
            worksheet.write(row, 5, o.hs, border_format)
            worksheet.write(row, 6, o.retenus, border_format)
            worksheet.write(row, 7, o.brut, border_format)
            worksheet.write(row, 8, o.brut_plafon, border_format)
            worksheet.write(row, 9, o.omsi, border_format)
            worksheet.write(row, 10, o.omsiemp, border_format)
            worksheet.write(row, 11, o.totalomsi, border_format)
            worksheet.write(row, 12, o.num_cnaps_emp if o.num_cnaps_emp else '', border_format)
            worksheet.write(row, 13, o.af, border_format)
            worksheet.write(row, 14, o.nbr_charge, border_format)
            worksheet.write(row, 15, o.cnaps, border_format)
            worksheet.write(row, 16, o.cnapsemp, border_format)
            worksheet.write(row, 17, o.total_cnaps, border_format)
            worksheet.write(row, 18, o.irsa, border_format)
            worksheet.write(row, 19, o.net, border_format)
            worksheet.write(row, 20, o.charge_pat, border_format)

            worksheet.write(row, 21, o.period, border_format)
            row += 1

        # TODO set total

        workbook.close()

        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', content_disposition(filename))]
        return request.make_response(output, xlsheader)
