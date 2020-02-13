# -*- coding: UTF-8 -*-
# by Rado - Ingenosya

import datetime
import io

import xlsxwriter

from odoo import http
from odoo.http import request


class ExportReportIrsaController(http.Controller):

    def setColumnWidth(self, worksheet, workbook):
        pass

    def head(self, workbook, worksheet, year, month, company_id=None):
        # styles
        middle = workbook.add_format({'align': "center", "valign": "vcenter"})
        bold_middle = workbook.add_format({'bold': True, 'align': "center", "valign": "vcenter"})

        # statics data
        worksheet.merge_range('B1:C1', u'Nom ou raison sociale de l\'organisme payeur')
        worksheet.write(0, 3, 'profession')
        worksheet.merge_range('E1:N1', u'REPOBLIKAN\' I MADAGASIKARA', middle)
        worksheet.merge_range('O2:R2', u'Etat à envoyer à l\'adresse suivante')
        worksheet.merge_range('G3:L3', u'SERVICES DES CONTRIBUTIONS DIRECTES', bold_middle)
        worksheet.merge_range('B8:C8', u'Montant des salaires et assimilés payés')
        worksheet.merge_range('B9:C9', u'depuis le début de l\'année')
        worksheet.merge_range('B10:C10', u'Montant des salaires et assimilés payés')
        worksheet.merge_range('B11:C11', u'au titre de la période considérée')
        worksheet.merge_range('B13:C13', u'Montant cumulés')
        worksheet.write(12, 7, u'N° dossier :')
        worksheet.merge_range('O7:R7', u'Cadre réservé au service des contribut°')
        worksheet.write(9, 14, u'N° ordre :')
        worksheet.write(11, 14, u'Etat reçu le :')

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
            company_id.city if company_id.city else ''))
        worksheet.merge_range('B5:C5', u'N° statistique : %s' % (
            company_id.nstat if company_id.nstat else ''
        ))
        worksheet.write(13, 7, u'NI.F.: %s' % (company_id.nif if company_id.nif else ''))

        return None

    def writePayslip(self, workbook, worksheet, row, col, payslip, total):
        # init variable
        # use something else sum()
        basic2 = payslip.contract_id.wage
        prm = sum(payslip.line_ids.filtered(lambda x: x.code == 'PRM').mapped('total'))
        hs = sum(payslip.line_ids.filtered(lambda x: x.code in ['HS1', 'HS2']).mapped('quantity'))
        preavis = payslip.preavis if payslip.stc else 0
        gross = sum(payslip.line_ids.filtered(lambda x: x.code == 'GROSS').mapped('total'))
        cnaps_emp = sum(payslip.line_ids.filtered(lambda x: x.code == 'CNAPS_EMP').mapped('total'))
        ostie_emp = sum(payslip.line_ids.filtered(lambda x: x.code == 'OMSI_EMP').mapped('total'))
        net = sum(payslip.line_ids.filtered(lambda x: x.code == 'NET').mapped('total'))
        irsa = sum(payslip.line_ids.filtered(lambda x: x.code == 'IRSA').mapped('total'))

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

        worksheet.merge_range(row, col, row, col + 1, '%s' % (payslip.employee_id.name))
        worksheet.write(row, col + 2, '%s' % (payslip.employee_id.num_cnaps_emp if payslip.employee_id.num_cnaps_emp else ''))
        worksheet.write_number(row, col + 3, payslip.contract_id.number_of_hours)
        worksheet.write_number(row, col + 4, basic2)
        worksheet.write_number(row, col + 5, prm)
        worksheet.write_number(row, col + 6, hs)
        worksheet.write_number(row, col + 7, 21)
        worksheet.write_number(row, col + 8, preavis)
        worksheet.write_number(row, col + 9, gross)
        worksheet.write_number(row, col + 10, cnaps_emp)
        worksheet.write_number(row, col + 11, ostie_emp)
        worksheet.write_number(row, col + 12, net)
        worksheet.write_number(row, col + 13, 9999)
        worksheet.write_number(row, col + 14, irsa)
        worksheet.write_number(row, col + 15, 5000)

    def body(self, workbook, worksheet, payslips, total):
        worksheet.merge_range('B16:C17', u"Noms & Prénoms")
        worksheet.merge_range('D16:D17', u'N° CNaPS')
        worksheet.merge_range('E16:E17', u'Tps de travail')
        worksheet.merge_range('F16:F17', u'Salaire de base')
        worksheet.merge_range('G16:G17', u'Primes & gratification')
        worksheet.merge_range('H16:H17', u'Heures supplémentaire')
        worksheet.merge_range('I16:I17', u'Congés')
        worksheet.merge_range('J16:J17', u'Préavis')
        worksheet.merge_range('K16:K17', u'Salaire brut')
        worksheet.merge_range('L16:M16', u'Cotisations')
        worksheet.write(16, 11, u'CNaPS')
        worksheet.write(16, 12, u'OSTIE')
        worksheet.merge_range('N16:N17', u'Salaire Net')
        worksheet.merge_range('O16:O17', u'Montant imposable')
        worksheet.merge_range('P16:P17', u'Impôts corresp.')
        worksheet.merge_range('Q16:Q17', u'Déduction enfant')
        worksheet.merge_range('R16:R17', u'Impôts nets')

        for row, payslip in enumerate(payslips):
            self.writePayslip(workbook, worksheet, row + 17, 1, payslip, total)

        # define row col
        row = 16 + len(payslips)
        col = 5
        worksheet.write_number(row + 1, col, total['basic2'])
        worksheet.write_number(row + 1, col + 1, total['prm'])
        worksheet.write_number(row + 1, col + 2, total['hs'])
        worksheet.write_number(row + 1, col + 3, total['conge'])
        worksheet.write_number(row + 1, col + 4, total['preavis'])
        worksheet.write_number(row + 1, col + 5, total['gross'])
        worksheet.write_number(row + 1, col + 6, total['cnaps_emp'])
        worksheet.write_number(row + 1, col + 7, total['ostie_emp'])
        worksheet.write_number(row + 1, col + 8, total['net'])
        worksheet.write_number(row + 1, col + 9, total['mimpo'])
        worksheet.write_number(row + 1, col + 10, total['irsa'])
        worksheet.write_number(row + 1, col + 11, total['enfant'])
        worksheet.write_number(row + 1, col + 12, total['impnet'])

    # main function
    def fulfill(self, workbook, worksheet, payslips, year, month, company_id=None):
        total = {
            'prm': 0, 'gross': 0, 'hs': 0,
            'conge': 0, 'preavis': 0, 'basic2': 0,
            'cnaps_emp': 0, 'ostie_emp': 0, 'net': 0,
            'mimpo': 0, 'enfant': 0, 'irsa': 0, 'impnet': 0
        }
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
