# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import http
from odoo.http import request
import xlsxwriter as xlsxwriter
import io
from ..models.cnaps_reportexcel import DICT_MONTH


class ExportReportIrsaController(http.Controller):

    @http.route('/web/binary/download_report_irsa_file', type='http', auth="public")
    def generateIrsa_excel(self, line_irsa, comp):
        line_ = literal_eval(line_irsa)
        comp_ = literal_eval(comp)
        filename = "IRSA.xlsx"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.denominated_irsa(workbook, line_, comp_)
        workbook.close()
        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % filename)]
        return request.make_response(output, xlsheader)

    def style(self, workbook, align, size, bold, border):
        return workbook.add_format({
            'text_wrap': True,
            'border': border,
            'align': align,
            'valign': 'vcenter',
            'font_size': size,
            'bold': bold,
        })

    def style_number(self, workbook, bol):
        bold_ = workbook.add_format({
            'num_format': '###0.00',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 8,
            'bold': bol,
            'border':1,
        })
        return bold_

    def width(self, worksheet):
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 5)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:I', 10)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:T', 10)
        worksheet.set_column('U:Y', 12)

    def denominated_irsa(self, workbook, line_, comp_):
        worksheet = workbook.add_worksheet("IRSA_SAPT")
        self.width(worksheet)
        # worksheet.freeze_panes(12, 3)
        worksheet.merge_range('A1:D1', 'SECRETARIAT GENERAL', self.style(workbook, 'center', 10, True, 0))
        worksheet.merge_range('A2:D2', 'DIRECTION GENERALE DES IMPOTS', self.style(workbook, 'center', 10, True, 0))
        worksheet.merge_range('A3:D3', 'DIRECTION DES GRANDES ENTREPRISES', self.style(workbook, 'center', 10, True, 0))
        worksheet.merge_range('I9:X9', 'ETAT NOMINATIF DES TRAITEMENTS, SALAIRES ET ASSIMILES PAYES',
                              self.style(workbook, 'left', 12, True, 0))
        worksheet.write('I10', 'PERIODE :', self.style(workbook, 'right', 10, True, 0))
        worksheet.write('J10', comp_['m'], self.style(workbook, 'left', 8, False, 0))
        worksheet.write('I11', 'ANNEE :', self.style(workbook, 'right', 10, True, 0))
        worksheet.write('J11', comp_['y'], self.style(workbook, 'left', 8, False, 0))
        worksheet.merge_range('B13:D13', 'NOM OU RAISON SOCIALE : {}'.format(comp_['name']), self.style(workbook, 'left', 12, True, 0))
        worksheet.merge_range('B14:D14', 'Adresse : {}'.format(comp_['address']), self.style(workbook, 'left', 12, True, 0))
        # table
        worksheet.merge_range('A17:A18', u'N° Ordre :', self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('B17:B18', u"N° d'affiliation (CNaPS) :", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('C17:C18', "sexe", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('D17:D18', u"Nom et prénom", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('E17:E18', u"CIN / Carte de résident", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('F17:F18', "Date de naissance", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('G17:G18', "Adresse", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('H17:H18', "Date d'embauche", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('I17:I18', u"Date de débauchage", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('J17:J18', "Fonction", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('K16:T16', None, self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('K17:K18', "Salaire de base", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('L17:M17', u"Indemnités", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('N17:Q17', "Avantages en nature", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('L18', "Imposables", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('M18', "Non imposables", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('N18', "Vehicule", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('O18', "Logement", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('P18', "Domestiques", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('Q18', "Autres", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('R17:R18', "Heures suppl.", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('S17:S18', "Primes et gratification", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('T17:T18', "Autre", self.style(workbook, 'center', 8, True, 1))
        worksheet.write('U16', "REVENUS IMPOSABLES", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('U17:U18', "Salaire brut", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('V16:X16', u"Déduction", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('V17:V18', "CnaPS", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('W17:W18', u"OSTIE ou assimilé", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('X17:X18', "Salaire net", self.style(workbook, 'center', 8, True, 1))
        worksheet.merge_range('Y17:Y18', u"Impôt dû", self.style(workbook, 'center', 8, True, 1))

        self.line_irsa(workbook, worksheet, 18, 1, line_, 'num_cnaps', 'left')
        self.line_irsa(workbook, worksheet, 18, 2, line_, 'sex', 'center')
        self.line_irsa2(workbook, worksheet, 18, 3, line_, 'name', 'first_name', 'left')
        self.line_irsa(workbook, worksheet, 18, 4, line_, 'num_cin', 'center')
        self.line_irsa(workbook, worksheet, 18, 5, line_, 'place_of_birth', 'center')
        self.line_irsa2(workbook, worksheet, 18, 6, line_, 'address', 'street', 'center')
        self.line_irsa(workbook, worksheet, 18, 7, line_, 'date_start', 'left')
        self.line_irsa(workbook, worksheet, 18, 8, line_, 'date_end', 'center')
        self.line_irsa(workbook, worksheet, 18, 9, line_, 'job', 'center')
        self.line_irsa3(workbook, worksheet, 18, 10, line_, 'wage')
        self.line_irsa3(workbook, worksheet, 18, 20, line_, 'gross')
        self.line_irsa3(workbook, worksheet, 18, 21, line_, 'cnaps_emp')
        self.line_irsa3(workbook, worksheet, 18, 22, line_, 'osmi_emp')
        self.line_irsa3(workbook, worksheet, 18, 23, line_, 'net')
        self.line_irsa3(workbook, worksheet, 18, 24, line_, 'irsa')

        # empty
        self.line_irsa(workbook, worksheet, 18, 0, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 11, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 12, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 13, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 14, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 15, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 16, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 17, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 18, line_, 'vide', 'center')
        self.line_irsa(workbook, worksheet, 18, 19, line_, 'vide', 'center')
        len_irsa_line = len(line_)
        worksheet.write(len_irsa_line + 18, 0, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 1, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 2, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 3, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 4, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 5, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 6, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 7, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 8, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 9, None, self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 11, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 12, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 13, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 14, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 15, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 16, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 17, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 18, None,self.style(workbook, 'center', 8, True, 1))
        worksheet.write(len_irsa_line + 18, 19, None,self.style(workbook, 'center', 8, True, 1))
        #total
        worksheet.write_formula(len_irsa_line + 18, 10, '=SUM(K19:K{})'.format(len_irsa_line + 18), self.style_number(workbook, True))
        worksheet.write_formula(len_irsa_line + 18, 20, '=SUM(U19:U{})'.format(len_irsa_line + 18), self.style_number(workbook, True))
        worksheet.write_formula(len_irsa_line + 18, 21, '=SUM(V19:V{})'.format(len_irsa_line + 18), self.style_number(workbook, True))
        worksheet.write_formula(len_irsa_line + 18, 22, '=SUM(W19:W{})'.format(len_irsa_line + 18), self.style_number(workbook, True))
        worksheet.write_formula(len_irsa_line + 18, 23, '=SUM(X19:X{})'.format(len_irsa_line + 18), self.style_number(workbook, True))
        worksheet.write_formula(len_irsa_line + 18, 24, '=SUM(Y19:Y{})'.format(len_irsa_line + 18), self.style_number(workbook, True))

    def line_irsa(self, workbook, worksheet, row, col, fieldlist, field, align):
        i = 0
        for val in fieldlist:
            worksheet.write(row, col, fieldlist[i][field], self.style(workbook, align, 8, False, 1))
            row += 1
            i += 1

    def line_irsa2(self, workbook, worksheet, row, col, fieldlist, field1, field2, align):
        i = 0
        for val in fieldlist:
            worksheet.write(row, col, fieldlist[i][field1] + ' ' + fieldlist[i][field2],self.style(workbook, align, 8, False, 1))
            row += 1
            i += 1

    def line_irsa3(self, workbook, worksheet, row, col, fieldlist, field):
        i = 0
        for val in fieldlist:
            worksheet.write(row, col, fieldlist[i][field],self.style_number(workbook, False))
            row += 1
            i += 1