# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import http
from odoo.http import request
import xlsxwriter as xlsxwriter
import io
from ..models.cnaps_reportexcel import DICT_MONTH


class ExportReportCnapsController(http.Controller):
    """Function to export New Product Excel """

    @http.route('/web/binary/download_report_cnaps_file', type='http', auth="public")
    def download_report_cnaps_file(self, p, m, c, y, data_month1, data_month2, data_month3, plf, comp_inf, fmfp,
                                   **args):
        filename = "CNAPS.xlsx"
        output = io.BytesIO()
        fmfp_ = literal_eval(fmfp)
        comp_inf_ = literal_eval(comp_inf)
        workbook = xlsxwriter.Workbook(output)
        bold = workbook.add_format({'bold': True, "font_size": 10})
        full_border = workbook.add_format({
            "border": 1,
            "border_color": "#171C1E",
            "font_size": 10
        })
        self.report_excel_employer(workbook, p, m, c, y, bold, full_border, data_month1, data_month2, data_month3, plf,
                                   comp_inf_, fmfp_)
        self.month(workbook, data_month1, 1, plf)
        self.month(workbook, data_month2, 2, plf)
        self.month(workbook, data_month3, 3, plf)
        workbook.close()
        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % filename)]
        return request.make_response(output, xlsheader)

    def m_fmt(self, workbook, align):
        return workbook.add_format({'num_format': '###0.00', 'font_size': 10, "border": 1, 'align': align})

    def report_excel_employer(self, workbook, p, m, c, y, bold, full_border, data_month1, data_month2, data_month3,
                              plf, comp_inf_, fmfp):
        left = workbook.add_format({'font_size': 10})
        m_fmt = workbook.add_format({'num_format': '###0.00', 'font_size': 10, "border": 1, "align": "right"})
        month = literal_eval(m)
        count_eff = literal_eval(c)
        annee = literal_eval(y)
        plf = literal_eval(plf)
        partner = request.env['res.partner'].browse([int(p)])
        month_rank = DICT_MONTH.keys()[DICT_MONTH.values().index(str(month['mth1']))]
        periode_et_annee = month_rank + "-" + annee['y']
        worksheet_emp = workbook.add_worksheet("EMPOYEUR")
        worksheet_emp.set_column('A:A', 5)
        worksheet_emp.set_column('B:B', 30)
        worksheet_emp.set_column('C:F', 20)
        worksheet_emp.write('A1', "RENSEIGNEMENTS SUR L'EMPLOYEUR", bold)
        worksheet_emp.write('B4', u"N° MATRICULE", left)
        worksheet_emp.write('C4', comp_inf_['num_cnaps'], left)
        worksheet_emp.write('B5', "RAISON SOCIALE", left)
        worksheet_emp.write('C5', comp_inf_['name'], left)
        worksheet_emp.write('B6', u"N° NIF", left)
        worksheet_emp.write('C6', comp_inf_['nif'], left)
        worksheet_emp.write('B7', "ADRESSE", left)
        worksheet_emp.write('C7', comp_inf_['address'], left)
        worksheet_emp.write('B8', u"Téléphone :", left)
        worksheet_emp.write('C8', comp_inf_['tel'], left)
        worksheet_emp.write('B9', "E-mail", left)
        worksheet_emp.write('C9', comp_inf_['email'], left)
        worksheet_emp.write('A11', 'COTISATIONS', bold)
        worksheet_emp.write('B12', 'periode et annee', left)
        worksheet_emp.write('C12', periode_et_annee, full_border)
        worksheet_emp.write('B13', "Reference de paiement", left)
        worksheet_emp.write('C13', "Virement bancaire", full_border)
        worksheet_emp.write('B15', "Taux Employeur", left)
        worksheet_emp.write('B16', "Taux Travailleur", left)
        worksheet_emp.write('B17', "Taux Cotisation Formation", left)
        worksheet_emp.write('C15', str(comp_inf_['cotisation_cnaps_patr']) + '%', full_border)
        worksheet_emp.write('C16', str(comp_inf_['cotisation_cnaps_emp']) + '%', full_border)
        worksheet_emp.write('C17', u"1%", full_border)
        worksheet_emp.write('A19', u"MOIS CONCERNE", bold)
        worksheet_emp.write('A21', "RECAPITULATION", bold)
        worksheet_emp.write('C19', month['mth1'].upper(), full_border)
        worksheet_emp.write('D19', month['mth2'].upper(), full_border)
        worksheet_emp.write('E19', month['mth3'].upper(), full_border)
        worksheet_emp.write('B23', "Effectif mensuel(OBLIGATOIRE)", full_border)
        worksheet_emp.write('C23', int(count_eff['count_mth1']), full_border)
        worksheet_emp.write('D23', int(count_eff['count_mth2']), full_border)
        worksheet_emp.write('E23', int(count_eff['count_mth3']), full_border)
        worksheet_emp.write('B24', u"Totaux Salaires plafonnés", full_border)
        worksheet_emp.write('B25', "Cotisations Employeur", full_border)
        n1 = literal_eval(data_month1)
        n2 = literal_eval(data_month2)
        n3 = literal_eval(data_month3)
        worksheet_emp.write_formula('C24', "='Mois 1'!L{}".format(len(n1) + 3), m_fmt)
        worksheet_emp.write_formula('D24', "='Mois 2'!L{}".format(len(n2) + 3), m_fmt)
        worksheet_emp.write_formula('E24', "='Mois 3'!L{}".format(len(n3) + 3), m_fmt)
        worksheet_emp.write_formula('C25', "='Mois 1'!M{}".format(len(n1) + 3), m_fmt)
        worksheet_emp.write_formula('D25', "='Mois 2'!M{}".format(len(n2) + 3), m_fmt)
        worksheet_emp.write_formula('E25', "='Mois 3'!M{}".format(len(n3) + 3), m_fmt)
        worksheet_emp.write('B26', "Cotisations travailleurs", full_border)
        worksheet_emp.write_formula('C26', "='Mois 1'!N{}".format(len(n1) + 3), m_fmt)
        worksheet_emp.write_formula('D26', "='Mois 2'!N{}".format(len(n2) + 3), m_fmt)
        worksheet_emp.write_formula('E26', "='Mois 3'!N{}".format(len(n3) + 3), m_fmt)
        worksheet_emp.write('B27', "Cotisations formations", full_border)
        worksheet_emp.write('C27', sum([data1['cnaps_fmfp'] for data1 in n1]), m_fmt)
        worksheet_emp.write('D27', sum([data2['cnaps_fmfp'] for data2 in n2]), m_fmt)
        worksheet_emp.write('E27', sum([data3['cnaps_fmfp'] for data2 in n3]), m_fmt)
        worksheet_emp.write('F22', "TOTAUX", self.bold(workbook, 'left', 10, 0, True))
        worksheet_emp.write_formula('F23', "=sum(C23:E23)", full_border)
        worksheet_emp.write_formula('F24', "=sum(C24:E24)", m_fmt)
        worksheet_emp.write_formula('F25', "=sum(C25:E25)", m_fmt)
        worksheet_emp.write_formula('F26', "=sum(C26:E26)", m_fmt)
        worksheet_emp.write_formula('F27', "=sum(C27:E27)", m_fmt)

        # cotisation fmmfp
        # worksheet_emp.write('A27', u'COTISATIONS FMFP', self.bold(workbook, 'left', 10, 0, True))
        # worksheet_emp.write('B28', u'Année et periode', self.bold(workbook, 'left', 10, 0, False))
        # worksheet_emp.write('C28', periode_et_annee, full_border)
        # worksheet_emp.write('B29', u'Taux Employeur', self.bold(workbook, 'left', 10, 0, False))
        # worksheet_emp.write('C29', str(plf['patr']) + '%', full_border)

        worksheet_emp.write('A29', u'RECAPITULATION', self.bold(workbook, 'left', 10, 0, True))
        worksheet_emp.write('B31', u'MOIS CONCERNE', self.bold(workbook, 'left', 10, 1, False))
        worksheet_emp.write('C31', month['mth1'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write('D31', month['mth2'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write('E31', month['mth3'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write('F31', u'TOTAUX', self.bold(workbook, 'left', 10, 1, True))
        worksheet_emp.write('B32', u'Effectif mensuel(OBLIGATOIRE)', self.bold(workbook, 'left', 10, 1, False))
        worksheet_emp.write('C32', fmfp['fmfp1']['nb_fmfp'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write('D32', fmfp['fmfp2']['nb_fmfp'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write('E32', fmfp['fmfp3']['nb_fmfp'], self.bold(workbook, 'center', 10, 1, False))
        worksheet_emp.write_formula('F32', '=SUM(C32:E32)', self.bold(workbook, 'left', 10, 1, False))
        worksheet_emp.write('B33', u'Totaux Salaire plafonnées', self.bold(workbook, 'left', 10, 1, False))
        worksheet_emp.write('C33', fmfp['fmfp1']['m_fmfp'], self.style_number(workbook, False))
        worksheet_emp.write('D33', fmfp['fmfp2']['m_fmfp'], self.style_number(workbook, False))
        worksheet_emp.write('E33', fmfp['fmfp3']['m_fmfp'], self.style_number(workbook, False))
        worksheet_emp.write_formula('F33', '=SUM(C33:E33)', self.style_number(workbook, False))
        worksheet_emp.write('B33', u'Cotisation Employeur', self.bold(workbook, 'left', 10, 1, False))
        worksheet_emp.write_formula('C34', '=C33*{}%'.format(plf['emp']), self.style_number(workbook, False))
        worksheet_emp.write_formula('D34', '=D33*{}%'.format(plf['emp']), self.style_number(workbook, False))
        worksheet_emp.write_formula('E34', '=E33*{}%'.format(plf['emp']), self.style_number(workbook, False))
        worksheet_emp.write_formula('F34', '=SUM(C34:E34)', self.style_number(workbook, False))

    def style_number(self, workbook, bol):
        bold_ = workbook.add_format({
            'num_format': '###0.00',
            'align': 'right',
            'valign': 'vcenter',
            'font_size': 8,
            'bold': bol,
            'border':1,
        })
        return bold_

    def bold(self, workbook, align, size, border, bol):
        bold_ = workbook.add_format({
            'align': align,
            'valign': 'vcenter',
            'font_size': size,
            'bold': bol,
            'border': border,
        })
        return bold_

    # self.month(workbook, data_month1, 1)
    def month(self, workbook, data_month, n, plf):
        worksheet_mth = workbook.add_worksheet('%s %s' % ('Mois', n))
        merge_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 9
        })
        align_center = workbook.add_format({
            'align': 'center',
            "border": 1,
            "border_color": "#171C1E"
        })
        wrap = workbook.add_format({
            'text_wrap': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',

        })

        left = workbook.add_format({
            'text_wrap': True,
            'border': 1,
            'align': 'center',
            'valign': 'left',
            'font_size': 9
        })

        rigth = workbook.add_format({
            'num_format': '###0.00',
            'text_wrap': True,
            'border': 1,
            'align': 'rigth',
            'valign': 'vcenter',
            'font_size': 9
        })

        # we right dynamic data hera
        month = literal_eval(data_month)
        cl = len(month)
        self.cnaps_cell(worksheet_mth, 2, 0, month, 'period', left)
        self.cnaps_cell(worksheet_mth, 2, 1, month, 'num_cnaps', left)
        self.cnaps_cell(worksheet_mth, 2, 2, month, 'name', left)
        self.cnaps_cell(worksheet_mth, 2, 3, month, 'first_name', left)
        self.cnaps_cell(worksheet_mth, 2, 5, month, 'embauche', left)
        self.cnaps_cell(worksheet_mth, 2, 6, month, 'debauche', left)
        self.cnaps_cell(worksheet_mth, 2, 7, month, 'gross', rigth)
        self.cnaps_cell(worksheet_mth, 2, 9, month, 'tps_presence', rigth)
        self.cnaps_cell(worksheet_mth, 2, 12, month, 'cnaps_emp', rigth)
        self.cnaps_cell(worksheet_mth, 2, 13, month, 'cnaps_pat', rigth)
        self.cnaps_cell(worksheet_mth, 2, 15, month, 'num_cin', left)

        self.non_plafond(worksheet_mth, 2, 10, cl, rigth)
        self.plafond(worksheet_mth, literal_eval(plf), 2, 11, cl, rigth)

        # cnaps emp and patr
        # self.part(worksheet_mth, 2, 12, literal_eval(plf)['patr'], cl, rigth)
        # self.part(worksheet_mth, 2, 13, literal_eval(plf)['emp'], cl, rigth)

        # self.position_val(worksheet_mth, 2, 15, month_code['emp_cins')

        worksheet_mth.set_column('C:D', 20)
        worksheet_mth.set_column('K:L', 20)
        worksheet_mth.set_column('J:J', 15)
        worksheet_mth.set_column('H:I', 15)
        worksheet_mth.set_column('F:G', 15)
        worksheet_mth.set_column('M:O', 15)
        worksheet_mth.set_column('A:B', 25)
        worksheet_mth.set_column('E:E', 20)
        worksheet_mth.set_column('P:P', 20)
        worksheet_mth.merge_range('A1:A2', 'ANNEES-MOIS', merge_format)
        worksheet_mth.merge_range('B1:B2', u'N° CNaPSCL', merge_format)
        worksheet_mth.merge_range('C1:D1', 'TRAVAILLEUR', merge_format)
        worksheet_mth.merge_range('B1:B2', u'N° CNaPS', merge_format)
        worksheet_mth.write('C2', 'NOM', align_center)
        worksheet_mth.write('D2', 'PRENOMS', align_center)
        worksheet_mth.merge_range('E1:E2', 'Ref. Employeur ', merge_format)
        worksheet_mth.merge_range('F1:G1', 'DATE', merge_format)
        worksheet_mth.write('F2', 'ENTREE', align_center)
        worksheet_mth.write('G2', 'DEPART', align_center)
        worksheet_mth.merge_range('H1:I1', 'SALAIRE', merge_format)
        worksheet_mth.write('H2', 'DU MOIS', align_center)
        worksheet_mth.write('I2', 'AVANTAGE', align_center)
        worksheet_mth.merge_range('J1:J2', 'TEMPS PRESENCE', wrap)
        worksheet_mth.merge_range('K1:L1', 'TOTAL', merge_format)
        worksheet_mth.write('K2', 'NON PLAFONNE', align_center)
        worksheet_mth.write('L2', 'PLAFONNE', align_center)
        worksheet_mth.merge_range('M1:O1', 'COTISATION', merge_format)
        worksheet_mth.write('M2', 'EMPLOYEUR', align_center)
        worksheet_mth.write('N2', 'TRAVAILLEUR', align_center)
        worksheet_mth.write('O2', 'TOTAL', align_center)
        worksheet_mth.merge_range('P1:P2', u'N° CIN', merge_format)
        # ref employeur
        self.empty_col(worksheet_mth, 2, 4, cl, align_center)
        # avantage
        self.cnaps_cell(worksheet_mth, 2, 8, month, 'avantage', rigth)
        self.empty_col(worksheet_mth, 2, 14, cl, align_center)
        # total
        if cl == 0:
            cl = 1
        worksheet_mth.write('A{}'.format(cl + 3), 'TOTAL', rigth)
        worksheet_mth.write('B{}'.format(cl + 3), None, rigth)
        worksheet_mth.write('C{}'.format(cl + 3), None, rigth)
        worksheet_mth.write('D{}'.format(cl + 3), None, rigth)
        worksheet_mth.write('E{}'.format(cl + 3), None, rigth)
        worksheet_mth.write('F{}'.format(cl + 3), None, rigth)
        worksheet_mth.write('G{}'.format(cl + 3), None, rigth)
        worksheet_mth.write_formula('H{}'.format(cl + 3), "=sum(H3:H{})".format(cl + 2), rigth)
        worksheet_mth.write_formula('I{}'.format(cl + 3), "=sum(I3:I{})".format(cl + 2), rigth)
        worksheet_mth.write('J{}'.format(cl + 3), None, rigth)
        worksheet_mth.write_formula('K{}'.format(cl + 3), "=sum(K3:K{})".format(cl + 2), rigth)
        worksheet_mth.write_formula('L{}'.format(cl + 3), "=sum(L3:L{})".format(cl + 2), rigth)
        worksheet_mth.write_formula('M{}'.format(cl + 3), "=sum(M3:M{})".format(cl + 2), rigth)
        worksheet_mth.write_formula('N{}'.format(cl + 3), "=sum(N3:N{})".format(cl + 2), rigth)
        worksheet_mth.write_formula('O{}'.format(cl + 3), "=sum(O3:O{})".format(cl + 2), rigth)
        worksheet_mth.write('P{}'.format(cl + 3), None, rigth)
        # total cotisation
        self.total_cot(worksheet_mth, 2, 14, cl, rigth)

    def position_month(self, worksheet, row, col, field_list, val):
        for key in field_list:
            worksheet.write(row, col, field_list[key][val])
            row += 1

    def position_mount(self, worksheet, row, col, field_list, field):
        for key in field_list[field]:
            worksheet.write(row, col, key[0])
            row += 1

    def cnaps_cell(self, worksheet, row, col, field_list, i, stl):
        for val in field_list:
            worksheet.write(row, col, val[i], stl)
            row += 1

    def non_plafond(self, worksheet, row, col, row_count, stl):
        v = 3
        for i in range(row_count):
            worksheet.write_formula(row, col, '=H{}+I{}'.format(v, v), stl)
            row += 1
            v += 1

    def total_cot(self, worksheet, row, col, row_count, stl):
        v = 3
        for i in range(row_count):
            worksheet.write_formula(row, col, '=M{}+N{}'.format(v, v), stl)
            row += 1
            v += 1

    def plafond(self, worksheet, plf, row, col, row_count, stl):
        rw = 3
        for i in range(row_count):
            worksheet.write_formula(row, col,
                                    '=IF(K{}<{},K{},{})'.format(rw, plf['plf_amount'], rw,
                                                                plf['plf_amount']), stl)
            row += 1
            rw += 1

    def part(self, worksheet, row, col, pat_emp, row_count, stl):
        rw = 3
        for i in range(row_count):
            worksheet.write_formula(row, col, 'L{}*{}%'.format(rw, pat_emp), stl)
            row += 1
            rw += 1

    def empty_col(self, worksheet, row, col, n, stl):
        for i in range(n):
            worksheet.write(row, col, None, stl)
            row += 1
