# -*- coding: UTF-8 -*-
# by Rado - Ingenosya

import datetime
import io

import xlsxwriter

from odoo import http
from odoo.http import request


class ExportReportIrsaController(http.Controller):

    def add_to_format(self, existing_format, dict_of_properties, workbook):
        """Give a format you want to extend and a dict of the properties you want to
        extend it with, and you get them returned in a single format"""
        new_dict = {}
        for key, value in existing_format.__dict__.iteritems():
            if (value != 0) and (value != {}) and (value != None):
                new_dict[key] = value
        del new_dict['escapes']

        return (workbook.add_format(dict(new_dict.items() + dict_of_properties.items())))

    def box(self, workbook, sheet_name, row_start, col_start, row_stop, col_stop):
        """Makes an RxC box. Use integers, not the 'A1' format"""

        rows = row_stop - row_start + 1
        cols = col_stop - col_start + 1

        for x in xrange((rows) * (cols)):  # Total number of cells in the rectangle

            box_form = workbook.add_format()  # The format resets each loop
            row = row_start + (x // cols)
            column = col_start + (x % cols)

            if x < (cols):  # If it's on the top row
                box_form = self.add_to_format(box_form, {'top': 1}, workbook)
            if x >= ((rows * cols) - cols):  # If it's on the bottom row
                box_form = self.add_to_format(box_form, {'bottom': 1}, workbook)
            if x % cols == 0:  # If it's on the left column
                box_form = self.add_to_format(box_form, {'left': 1}, workbook)
            if x % cols == (cols - 1):  # If it's on the right column
                box_form = self.add_to_format(box_form, {'right': 1}, workbook)

            sheet_name.write(row, column, "", box_form)

    def setColumnWidth(self, worksheet):
        worksheet.set_column('C:C', 20)
        worksheet.set_column('G:G', 5)
        worksheet.set_column('I:I', 5)
        worksheet.set_column('K:K', 5)
        worksheet.set_column('L:L', 5)

    def head(self, workbook, worksheet, year, month, company_id=None):
        # styles
        middle = workbook.add_format({'align': "center", "valign": "vcenter"})
        bold_middle = workbook.add_format({'bold': True, 'align': "center", "valign": "vcenter"})
        border_black = workbook.add_format({"border_color": "black", 'border': 1})
        border_left = workbook.add_format({"border_color": "black", 'left': 1})
        border_left_top = workbook.add_format({"border_color": "black", 'left': 1, 'top': 1})

        # cells with border
        self.box(workbook, worksheet, 2, 14, 4, 17)
        self.box(workbook, worksheet, 7, 14, 12, 17)
        self.box(workbook, worksheet, 3, 1, 5, 3)
        self.box(workbook, worksheet, 7, 1, 13, 3)

        # statics data
        worksheet.merge_range('B1:C1', u'Nom ou raison sociale de l\'organisme payeur', border_black)
        worksheet.write(0, 3, 'profession', border_black)
        worksheet.merge_range('E1:N1', u'REPOBLIKAN\' I MADAGASIKARA', middle)
        worksheet.merge_range('O2:R2', u'Etat à envoyer à l\'adresse suivante', border_black)
        worksheet.merge_range('G3:L3', u'SERVICES DES CONTRIBUTIONS DIRECTES', bold_middle)
        worksheet.merge_range('B8:C8', u'Montant des salaires et assimilés payés', border_left_top)
        worksheet.merge_range('B9:C9', u'depuis le début de l\'année', border_left)
        worksheet.merge_range('B10:C10', u'Montant des salaires et assimilés payés', border_left)
        worksheet.merge_range('B11:C11', u'au titre de la période considérée', border_left)
        worksheet.merge_range('B13:C13', u'Montant cumulés', border_left)
        worksheet.write(12, 7, u'N° dossier :')
        worksheet.merge_range('O7:R7', u'Cadre réservé au service des contribut°', border_black)
        worksheet.write(9, 14, u'N° ordre :', border_left)
        worksheet.write(11, 14, u'Etat reçu le :', border_left)

        # dynamic data
        # create date with data
        date = datetime.datetime.strptime("%s %s" % (year, month), "%Y %m")
        worksheet.write(6, 7, 'ANNEE : %s' % date.strftime("%Y"))
        # fuck unicode in python 2
        n = unicode(date.strftime("%B").upper(), 'utf-8', 'replace')
        worksheet.write(8, 7, u'AU TITRE DU MOIS : {0}'.format(n))
        worksheet.write(10, 7, 'SEMESTRE : %s' % 'PREMIER' if date.strftime("%m") <= '06' else 'SECOND')

        if company_id is None:
            return None

        # dynamic data
        worksheet.write(1, 1, company_id.name)
        worksheet.write(1, 3, 'achat-vente')
        worksheet.merge_range('B4:C4', u'Adresse : %s %s' % (
            company_id.street if company_id.street else '',
            company_id.city if company_id.city else ''), border_left_top)
        worksheet.merge_range('B5:C5', u'N° statistique : %s' % (
            company_id.nstat if company_id.nstat else ''
        ), border_left)
        worksheet.write(13, 7, u'NI.F.: %s' % (company_id.nif if company_id.nif else ''))

        return None

    def writePayslip(self, workbook, worksheet, row, col, payslip, total):
        # styles
        border_black = workbook.add_format({"border_color": "black", 'border': 1})

        # init variable
        # use something else sum()
        basic2 = payslip.contract_id.wage
        prm = sum(payslip.line_ids.filtered(lambda x: x.code == 'PRM').mapped('total'))
        hs = sum(payslip.line_ids.filtered(lambda x: x.code in ('HS1', 'HS2', 'HMNUIT', 'HMDIM', 'HMDIM', 'HMJF')).mapped('total'))
        preavis = payslip.preavis if payslip.stc else 0
        gross = sum(payslip.line_ids.filtered(lambda x: x.code == 'GROSS').mapped('total'))
        cnaps_emp = sum(payslip.line_ids.filtered(lambda x: x.code == 'CNAPS_EMP').mapped('total'))
        ostie_emp = sum(payslip.line_ids.filtered(lambda x: x.code == 'OMSI_EMP').mapped('total'))
        net = sum(payslip.line_ids.filtered(lambda x: x.code == 'NET').mapped('total'))
        mimpo = sum(payslip.line_ids.filtered(lambda x: x.code == 'INFO').mapped('total'))
        irsa = sum(payslip.line_ids.filtered(lambda x: x.code == 'IRSA').mapped('total'))
        enfant = payslip.employee_id.children * payslip.company_id.abat_irsa
        impnet = irsa - enfant

        # compute sum
        total['basic2'] += basic2
        total['prm'] += prm
        total['hs'] += hs
        total['preavis'] += preavis
        total['gross'] += gross
        total['cnaps_emp'] += cnaps_emp
        total['ostie_emp'] += ostie_emp
        total['net'] += net
        total['irsa'] += irsa
        total['mimpo'] += mimpo # à revoir
        total['conge'] += payslip.employee_id.remaining_leaves
        total['enfant'] += enfant
        total['impnet'] += impnet

        worksheet.merge_range(row, col, row, col + 1, '%s' % (payslip.employee_id.name), border_black)
        worksheet.write(row, col + 2, '%s' % (payslip.employee_id.job_id.name if payslip.employee_id.job_id.name else ''), border_black)
        worksheet.write(row, col + 3, '%s' % (payslip.employee_id.address_home_id.street if payslip.employee_id.address_home_id.street else ''), border_black)
        worksheet.write(row, col + 4, '%s' % (payslip.employee_id.num_cnaps_emp if payslip.employee_id.num_cnaps_emp else ''), border_black)
        worksheet.write_number(row, col + 5, payslip.contract_id.number_of_hours, border_black)
        worksheet.write_number(row, col + 6, basic2, border_black)
        worksheet.write_number(row, col + 7, prm, border_black)
        worksheet.write_number(row, col + 8, hs, border_black)
        worksheet.write_number(row, col + 9, payslip.employee_id.remaining_leaves, border_black)
        worksheet.write_number(row, col + 10, preavis, border_black)
        worksheet.write_number(row, col + 11, gross, border_black)
        worksheet.write_number(row, col + 12, cnaps_emp, border_black)
        worksheet.write_number(row, col + 13, ostie_emp, border_black)
        worksheet.write_number(row, col + 14, net, border_black)
        worksheet.write_number(row, col + 15, mimpo, border_black)
        worksheet.write_number(row, col + 16, irsa, border_black)
        worksheet.write_number(row, col + 17, enfant, border_black)
        worksheet.write_number(row, col + 18, impnet, border_black)

    def body(self, workbook, worksheet, payslips, total):
        # styles
        border_black = workbook.add_format({"border_color": "black", 'border': 1})
        border_black_center = workbook.add_format({"border_color": "black", 'border': 1, 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})

        worksheet.merge_range('B16:C17', u"Noms & Prénoms", border_black)
        worksheet.merge_range('D16:D17', u'Profession', border_black_center)
        worksheet.merge_range('E16:E17', u'Adresse', border_black_center)
        worksheet.merge_range('F16:F17', u'N° CNaPS', border_black_center)
        worksheet.merge_range('G16:G17', u'Tps de travail', border_black_center)
        worksheet.merge_range('H16:H17', u'Salaire de base', border_black_center)
        worksheet.merge_range('I16:I17', u'Primes & gratification', border_black_center)
        worksheet.merge_range('J16:J17', u'Heures supplémentaire', border_black_center)
        worksheet.merge_range('K16:K17', u'Congés', border_black_center)
        worksheet.merge_range('L16:L17', u'Préavis', border_black_center)
        worksheet.merge_range('M16:M17', u'Salaire brut', border_black_center)
        worksheet.merge_range('N16:O16', u'Cotisations', border_black_center)
        worksheet.write(16, 13, u'CNaPS', border_black_center)
        worksheet.write(16, 14, u'OSTIE', border_black_center)
        worksheet.merge_range('P16:P17', u'Salaire Net', border_black_center)
        worksheet.merge_range('Q16:Q17', u'Montant imposable', border_black_center)
        worksheet.merge_range('R16:R17', u'Impôts corresp.', border_black_center)
        worksheet.merge_range('S16:S17', u'Déduction enfant', border_black_center)
        worksheet.merge_range('T16:T17', u'Impôts nets', border_black_center)

        for row, payslip in enumerate(payslips):
            self.writePayslip(workbook, worksheet, row + 17, 1, payslip, total)

        # define row col
        row = 16 + len(payslips)
        col = 7
        worksheet.write(row + 1, col - 6, "", border_black)
        worksheet.write(row + 1, col - 5, "", border_black)
        worksheet.write(row + 1, col - 4, "", border_black)
        worksheet.write(row + 1, col - 3, "", border_black)
        worksheet.write(row + 1, col - 2, "", border_black)
        worksheet.write(row + 1, col - 1, "", border_black)
        worksheet.write_number(row + 1, col, total['basic2'], border_black)
        worksheet.write_number(row + 1, col + 1, total['prm'], border_black)
        worksheet.write_number(row + 1, col + 2, total['hs'], border_black)
        worksheet.write_number(row + 1, col + 3, total['conge'], border_black)
        worksheet.write_number(row + 1, col + 4, total['preavis'], border_black)
        worksheet.write_number(row + 1, col + 5, total['gross'], border_black)
        worksheet.write_number(row + 1, col + 6, total['cnaps_emp'], border_black)
        worksheet.write_number(row + 1, col + 7, total['ostie_emp'], border_black)
        worksheet.write_number(row + 1, col + 8, total['net'], border_black)
        worksheet.write_number(row + 1, col + 9, total['mimpo'], border_black)
        worksheet.write_number(row + 1, col + 10, total['irsa'], border_black)
        worksheet.write_number(row + 1, col + 11, total['enfant'], border_black)
        worksheet.write_number(row + 1, col + 12, total['impnet'], border_black)

    # main function
    def fulfill(self, workbook, worksheet, payslips, year, month, company_id=None):
        total = {
            'prm': 0, 'gross': 0, 'hs': 0,
            'conge': 0, 'preavis': 0, 'basic2': 0,
            'cnaps_emp': 0, 'ostie_emp': 0, 'net': 0,
            'mimpo': 0, 'enfant': 0, 'irsa': 0, 'impnet': 0,
        }
        self.setColumnWidth(worksheet)
        self.head(workbook, worksheet, year, month, company_id)
        self.body(workbook, worksheet, payslips, total)

    @http.route('/web/binary/download_report_irsa_file', type='http', auth="public")
    def generateIrsa_excel(self, year, month):
        filename = "IRSA.xlsx"
        output = io.BytesIO()
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("IRSA")

        # take periodic payslip
        payslips = request.env['hr.payslip'].search([('date_from', 'like', "%s-%s%s" % (year, month, '%'))])
        company_id = payslips[:1].company_id

        self.fulfill(workbook, worksheet, payslips, year, month, company_id)

        workbook.close()
        output.seek(0)

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % filename)]
        return request.make_response(output, xlsheader)
