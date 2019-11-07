# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import http
from odoo.http import request
import xlsxwriter as xlsxwriter
import io


class ExportReportOstieController(http.Controller):

    @http.route('/web/binary/download_report_ostie_file', type='http', auth="public")
    def download_report_ostie_file(self, sante, plf, comp_inf, y, eff, mc, plf32, trim, eft):  #
        plf = literal_eval(plf)

        filename = "OSTIE.xlsx"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        comp_inf_ = literal_eval(comp_inf)
        mc_ = literal_eval(mc)
        eff_ = literal_eval(eff)
        plf32_ = literal_eval(plf32)

        ostie_info = literal_eval(sante)
        row_count = len(ostie_info)

        self.report_excel_employer(workbook, sante, plf, comp_inf_, y, trim, eff_, row_count)  #
        self.recap_cotisation(workbook, comp_inf_, y, eff_, mc_, plf32_, plf, row_count)
        workbook.close()
        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % filename)]
        return request.make_response(output, xlsheader)

    def bold(self, workbook, align, size, border, bol):
        bold_ = workbook.add_format({
            'align': align,
            'valign': 'vcenter',
            'font_size': size,
            'bold': bol,
            'border': border,
        })
        return bold_

    def dis(self, workbook, align, border, bol):
        bold_ = workbook.add_format({
            'align': align,
            'valign': 'vcenter',
            'font_size': 10,
            'bold': bol,
            'border': border,
        })
        return bold_

    def dis2(self, workbook, align, border, bol):
        bold_ = workbook.add_format({
            'num_format': '###0.00',
            'align': align,
            'valign': 'vcenter',
            'font_size': 10,
            'bold': bol,
            'border': border,
        })
        return bold_

    def wrap(self, workbook, align):
        wrap_ = workbook.add_format({
            'text_wrap': True,
            'align': align,
            'valign': 'vcenter',
            'font_size': 8,
            'border': 1,

        })
        return wrap_

    def wrap2(self, workbook, align):
        wrap_ = workbook.add_format({
            'num_format': '###0.00',
            'text_wrap': True,
            'align': align,
            'valign': 'vcenter',
            'font_size': 8,
            'border': 1,

        })
        return wrap_

    def report_excel_employer(self, workbook, sante, plf, comp_inf, y, trim, eff, row_count):  #

        worksheet_ost = workbook.add_worksheet("DNS")
        wrap = workbook.add_format({
            'text_wrap': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 8
        })
        worksheet_ost.set_row(13, 30)
        self.style(worksheet_ost)
        self.show_ostie_info(worksheet_ost, sante, workbook, plf, comp_inf, wrap)

        topleft_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "top": 1,
            "left": 1,
            "top_color": "black",
            "left_color": "black",
            "font_size": 10,
            'bold': True,
        })
        toprigth_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "top": 1,
            "right": 1,
            "top_color": "black",
            "right_color": "black",
            'font_size': 10
        })

        left_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "left": 1,
            "left_color": "black",
            'font_size': 10,
            'bold': True,
        })

        left_border2 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "left": 1,
            "left_color": "black",
            'font_size': 8,
            'bold': True,
        })
        left_border3 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "left": 1,
            "left_color": "black",
            'font_size': 8,

        })
        right_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "right": 1,
            "right_color": "black",
            'font_size': 10
        })
        leftbotom_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "left": 1,
            "bottom": 1,
            "bottom_color": "black",
            "left_color": "black",
            'font_size': 8
        })
        rightbotom_border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "right": 1,
            "bottom": 1,
            "bottom_color": "black",
            "right_color": "black"
        })
        botom_border = workbook.add_format({
            "bottom": 1,
            "bottom_color": "black"
        })
        top_border = workbook.add_format({
            "bottom": 1,
            "top_color": "black"
        })
        top_bottom = workbook.add_format({
            "bottom": 1,
            "top": 1,
            "font_size": 10,
            "top_color": "black",
            "bottom_color": "black"
        })
        left_rigth = workbook.add_format({
            "left": 1,
            "right": 1,
            "font_size": 10,
            "left_color": "black",
            "right_color": "black",
            "align": "center"
        })

        left_rigth_bottom = workbook.add_format({
            "left": 1,
            "right": 1,
            "bottom": 1,
            "font_size": 10,
            "left_color": "black",
            "right_color": "black",
            "bottom_color": "black",
            "align": "center"
        })
        font_10 = workbook.add_format({
            "font_size": 10
        })

        worksheet_ost.merge_range('A1:E1', 'ORGANISATION SANITAIRE TANARIVIENNE INTER-ENTREPRISE',
                                  self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.merge_range('A2:E2', "O.S.T.I.E", self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.merge_range('G1:N1', "DECLARATION NOMINATIVE DES SALAIRES VERSES AU TITRE DU ",
                                  self.bold(workbook, 'right', 10, 0, True))
        worksheet_ost.write('O1', trim, self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.write('P1', "TRIMESTRE", self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.write('Q1', y, self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.merge_range('G3:H3', "CODE ADHERENT ", topleft_border)
        worksheet_ost.write('I3', comp_inf['matricule'], self.bold(workbook, 'center', 10, 0, False))
        worksheet_ost.merge_range('G4:H4', "Raison Sociale", left_border)
        worksheet_ost.merge_range('G5:H5', "Adresse :", left_border)
        worksheet_ost.merge_range('G6:H6', "Tel : {}".format(comp_inf['tel']), left_border)
        worksheet_ost.merge_range('I6:K6', "eMail : {}".format(comp_inf['email']),
                                  self.bold(workbook, 'center', 8, 0, True))
        worksheet_ost.write('G7', "STAT", left_border2)
        worksheet_ost.write('H7', comp_inf['stat'], left_border2)
        worksheet_ost.write('G8', "ACTIVITE", left_border2)
        worksheet_ost.write('L8', "REGIME", self.bold(workbook, 'center', 8, 0, True))
        worksheet_ost.merge_range('G9:H9', "Taux Employeur :", left_border3)
        worksheet_ost.write('M3', "FOLIO:", self.bold(workbook, 'right', 10, 0, True))
        worksheet_ost.merge_range('G10:H10', "N Cnaps Employeur ", left_border3)
        worksheet_ost.write('G11', "", leftbotom_border)
        worksheet_ost.write('H11', "", botom_border)
        worksheet_ost.write('I11', "", botom_border)
        worksheet_ost.write('J11', "", botom_border)
        worksheet_ost.write('K11', "", botom_border)
        worksheet_ost.write('L11', "", botom_border)
        worksheet_ost.write('M11', "", botom_border)
        worksheet_ost.write('I2', "", top_border)
        worksheet_ost.write('J2', "", top_border)
        worksheet_ost.write('K2', "", top_border)
        worksheet_ost.write('L2', "", top_border)
        worksheet_ost.write('M2', "", top_border)
        worksheet_ost.write('N3', "", toprigth_border)
        worksheet_ost.write('N4', "", right_border)
        worksheet_ost.write('N5', "", right_border)
        worksheet_ost.write('N6', "", right_border)
        worksheet_ost.write('N7', "", right_border)
        worksheet_ost.write('N8', "", right_border)
        worksheet_ost.write('N9', "", right_border)
        worksheet_ost.write('N10', "", right_border)
        worksheet_ost.write('N11', "", rightbotom_border)
        worksheet_ost.write('M8', "GENERAL", self.bold(workbook, 'center', 8, 0, True))
        worksheet_ost.write('A14', u"N°", wrap)
        worksheet_ost.write('B14', "MATRICULE", wrap)
        worksheet_ost.write('C14', "NOM DU TRAVAILLEUR", wrap)
        worksheet_ost.write('D14', "PRENOMS DU TRAVAILLEUR", wrap)
        worksheet_ost.write('E14', "SEXE", wrap)
        worksheet_ost.write('F14', "DATE DE NAISSANCE", wrap)
        worksheet_ost.write('G14', "DATE D'EMBAUCHE", wrap)
        worksheet_ost.write('H14', "DATE DE DEBAUCHE", wrap)
        worksheet_ost.write('I14', "FONCTION", wrap)
        worksheet_ost.write('J14', u"N° CNAPS", wrap)
        worksheet_ost.write('K14', u"N° CIN", wrap)
        worksheet_ost.write('L14', "SALAIRE 1er MOIS", wrap)
        worksheet_ost.write('M14', "SALAIRE 2eme MOIS", wrap)
        worksheet_ost.write('N14', "SALAIRE 3eme MOIS", wrap)
        worksheet_ost.write('O14', "TOTAUX SALAIRES NON PLAFONNES", wrap)
        worksheet_ost.write('P14', "TOTAUX SALAIRES PLAFONNES", wrap)
        worksheet_ost.write('Q14', "PART EMPLOYEUR 5%", wrap)
        worksheet_ost.write('R14', "PART TAVAILLEUR 1%", wrap)

        worksheet_ost.merge_range('A3:E3', u'Rue Dr Zamenhof Behoririka 101 ANTANANARIVO',
                                  self.bold(workbook, 'center', 8, 0, False))
        worksheet_ost.merge_range('A4:E4', u'Tél.: 22 265 78 / 22 274 76 / 22 251 42  FAX : 22 265 66',
                                  self.bold(workbook, 'center', 8, 0, False))
        worksheet_ost.merge_range('A5:E5', u'BP : 165 Antananarivo ',
                                  self.bold(workbook, 'center', 8, 0, False))
        worksheet_ost.merge_range('A6:E6', u'e-mail : sadhostie@moov.mg         site web : www.ostie.mg',
                                  self.bold(workbook, 'center', 8, 0, False))
        worksheet_ost.merge_range('A7:C7', u'BOA Andravoahangy   00009 05600 10762050010 23',
                                  self.bold(workbook, 'left', 8, 0, False))
        worksheet_ost.merge_range('A8:C8', u'BNI-CL Analakely  00005 00001 01232020200 71',
                                  self.bold(workbook, 'left', 8, 0, False))
        worksheet_ost.merge_range('A9:C9', u'BFV-SG  Antaninarenina  00008 00005 21000155438 43',
                                  self.bold(workbook, 'left', 8, 0, False))
        worksheet_ost.merge_range('A10:C10', u'BMOI Analamahitsy 00004 00003 01500800184 32',
                                  self.bold(workbook, 'left', 8, 0, False))
        worksheet_ost.merge_range('A11:C11', u'ACCES BANQUE Antaninandro  00011 00003 24100035111 77',
                                  self.bold(workbook, 'left', 8, 0, False))
        worksheet_ost.merge_range('A12:C12', u'ORANGE MONEY  032 24 704 67',
                                  self.bold(workbook, 'left', 8, 0, False))
        # explication des contenues des colonne
        nbl = row_count
        worksheet_ost.merge_range('B{}:D{}'.format(nbl + 17, nbl + 17), u'EXPLICATION DES CONTENUS DES COLONNES ',
                                  self.bold(workbook, 'left', 10, 0, True))
        worksheet_ost.write('B{}'.format(nbl + 19), u'COLONNE', self.bold(workbook, 'center', 10, 1, True))
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 19, nbl + 19), u'DESCRIPTION', top_bottom)
        worksheet_ost.write('H{}'.format(nbl + 19), u'EXEMPLE', self.bold(workbook, 'center', 10, 1, True))
        worksheet_ost.write('B{}'.format(nbl + 20), u'A', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 21), u'B', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 22), u'C', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 23), u'D', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 24), u'E', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 25), u'F', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 26), u'G', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 27), u'H', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 28), None, left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 29), u'I', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 30), u'J', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 31), None, left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 32), None, left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 33), u'K', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 34), u'L,M,N', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 35), None, left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 36), u'O', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 37), u'P', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 38), None, left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 39), u'P', left_rigth)
        worksheet_ost.write('B{}'.format(nbl + 40), u'Q', left_rigth_bottom)

        worksheet_ost.write('H{}'.format(nbl + 20), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 21), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 22), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 23), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 24), u'M ou F', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 25), u'02/06/1983', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 26), u'04/01/2017', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 27), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 28), u'04/01/2017', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 29), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 30), u'033546', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 31), u'12345678901K', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 32), u'564234', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 33), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 34), u'1234567', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 35), None, left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 36), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 37), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 38), None, left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 39), u'', left_rigth)
        worksheet_ost.write('H{}'.format(nbl + 40), u'', left_rigth_bottom)

        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 20, nbl + 20), u'Numéro chronologique', font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 21, nbl + 21), u"N° matricule du travailleur chez l'employeur",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 22, nbl + 22),
                                  u'Nom du travailleur : Toujours à renseigner, ne pas intervertir avec les prénoms',
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 23, nbl + 23),
                                  u'Prénoms du travailleur : A renseigner si existant, ne pas intervertir avec le nom',
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 24, nbl + 24), u'Sexe : Masculin ou Féminin', font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 25, nbl + 25),
                                  u'Date de naissance obligatoire. Mettre au format date JJ/MM/AAAA', font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 26, nbl + 26),
                                  u"Date d'embauche : mettre au format date JJ/MM/AAAA", font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 27, nbl + 27),
                                  u'Date de départ : A renseigner uniquement si le travailleur a été débauché au cours de ce',
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 28, nbl + 28), u'trimestre. Mettre au format date JJ/MM/AAAA',
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 29, nbl + 29), u'Fonction', font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 30, nbl + 30),
                                  u"N° CNaPS : N° d'affiliation du travailleur. Si le numéro comporte des zéros devant,",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 31, nbl + 31),
                                  u"tapez ces zéros. Ce numéro doit être renseigné sauf si le travailleur a été embauché au",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 32, nbl + 32),
                                  u"cours du trimestre, auquel cas, la date d'entrée et le n° CIN doivent être renseignés",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 33, nbl + 33),
                                  u"CIN : N° CIN du travailleur - N° passeport pour les expatriés", font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 34, nbl + 34),
                                  u"Salaire du mois : Montant du salaire du mois, non plafonné, en format nombre sans ",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 35, nbl + 35), u"séparation de milliers, donc cadré à droite",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 36, nbl + 36),
                                  u"Total non plafonné : Somme des colonnes L, M et N (format nombre)", font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 37, nbl + 37),
                                  u"Total plafonné : Si la valeur de L ou M ou N est supérieur au plafond règlementaire,",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 38, nbl + 38),
                                  u"faire la somme avec le plafond règlementaire, sinon mettre O (format nombre)",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 39, nbl + 39),
                                  u"Cotisation part employeur : Valeur de P à multiplier par le taux employeur en vigueur ",
                                  font_10)
        worksheet_ost.merge_range('C{}:G{}'.format(nbl + 40, nbl + 40),
                                  u"Cotisation part travailleur : Valeur de P à multiplier par le taux travailleur en vigueur ",
                                  top_border)

        # recommendation
        worksheet_ost.merge_range('K{}:L{}'.format(nbl + 17, nbl + 17), u"RECOMMANDATIONS :",
                                  self.bold(workbook, 'center', 10, 0, True))
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 19, nbl + 19), u"Toutes les colonnes doivent être remplies",
                                  font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 20, nbl + 20),
                                  u"Dans le cas contraire, le fichier sera retourné à l'employeur.", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 22, nbl + 22),
                                  u"Ne jamais insérer ni supprimer d'autres lignes à l'en-tête (ligne 1 à 14)", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 24, nbl + 24), u"Ne jamais insérer d'autres colonnes", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 26, nbl + 26), u"Ne pas intervertir les colonnes", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 28, nbl + 28), u"Mettre au majuscule les noms et prénoms",
                                  font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 30, nbl + 30), u"ainsi que les fonctions", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 32, nbl + 32),
                                  u"Faire apparaitre dans l'objet du mail ainsi que dans le nom de fichier", font_10)
        worksheet_ost.merge_range('J{}:O{}'.format(nbl + 34, nbl + 34),
                                  u"Ne pas oublier d'établir l'état récapitulatif (onglet RECAP COTISATION)", font_10)

    def style(self, worksheet):
        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 8)
        worksheet.set_column('E:E', 4)
        worksheet.set_column('C:D', 22)
        worksheet.set_column('F:H', 11)
        worksheet.set_column('I:I', 12)
        worksheet.set_column('J:R', 10)

    def show_ostie_info(self, worksheet, sante, workbook, plf, comp_inf, wrap):

        ostie_info = literal_eval(sante)
        row_count = len(ostie_info)
        self.line_number(worksheet, row_count, 14, 0, wrap)
        self.ostie_cell(worksheet, 14, 1, ostie_info, 'num_emp', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 2, ostie_info, 'name', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 3, ostie_info, 'prenom', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 4, ostie_info, 'sexe', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 5, ostie_info, 'date_naiss', self.wrap(workbook, 'right'))
        self.ostie_cell(worksheet, 14, 6, ostie_info, 'embauche', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 7, ostie_info, 'debauche', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 8, ostie_info, 'job', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 9, ostie_info, 'num_cnaps', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 10, ostie_info, 'num_cin', self.wrap(workbook, 'left'))
        self.ostie_cell(worksheet, 14, 11, ostie_info, 'salary1', self.wrap2(workbook, 'right'))
        self.ostie_cell(worksheet, 14, 12, ostie_info, 'salary2', self.wrap2(workbook, 'right'))
        self.ostie_cell(worksheet, 14, 13, ostie_info, 'salary3', self.wrap2(workbook, 'right'))
        self.non_plafond(worksheet, 14, 14, row_count, self.wrap2(workbook, 'right'))
        self.plafond(worksheet, plf, 14, 15, row_count, self.wrap2(workbook, 'right'))
        self.part(worksheet, 14, 16, 5, row_count, self.wrap2(workbook, 'right'))
        self.part(worksheet, 14, 17, 1, row_count, self.wrap2(workbook, 'right'))
        # information
        worksheet.merge_range('I4:K4', comp_inf['name'].upper(), self.bold(workbook, 'left', 11, 0, True))
        worksheet.merge_range('I5:J5', comp_inf['address'], self.bold(workbook, 'center', 8, 0, False))
        worksheet.write('I9', comp_inf['employer_rate'], self.bold(workbook, 'center', 8, 0, False))
        worksheet.write('J9', 'Travailleur :', self.bold(workbook, 'center', 8, 0, False))
        worksheet.write('L9', comp_inf['worker_rate'], self.bold(workbook, 'center', 8, 0, False))
        # total
        worksheet.merge_range('J{}:K{}'.format(row_count + 15, row_count + 15), 'TOTAUX', self.wrap(workbook, 'center'))
        worksheet.write_formula(row_count + 14, 11, '=SUM(L15:L{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 12, '=SUM(M15:M{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 13, '=SUM(N15:N{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 14, '=SUM(O15:O{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 15, '=SUM(P15:P{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 16, '=SUM(Q15:Q{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))
        worksheet.write_formula(row_count + 14, 17, '=SUM(R15:R{})'.format(row_count + 14),
                                self.wrap2(workbook, 'right'))

    def recap_cotisation(self, workbook, comp_inf, y, eff, mc, plf32_, plf, row_count):

        worksheet = workbook.add_worksheet('RECAP_COTISATION')
        worksheet.set_column('C:F', 20)
        worksheet.write("A1", "ETAT RECAPITULATIF DES DECLARATIONS NOMINATIVES DE SALAIRES",
                        self.dis(workbook, 'left', 0, True))
        worksheet.write("B3", "CODE ADHERENT", self.dis(workbook, 'left', 0, False))
        worksheet.write("B4", "RAISON SOCIALE", self.dis(workbook, 'left', 0, False))
        worksheet.write("B5", u"N Télphone", self.dis(workbook, 'left', 0, False))
        worksheet.write("B6", "ADRESSE", self.dis(workbook, 'left', 0, False))
        worksheet.write("B7", "Adresse mail", self.dis(workbook, 'left', 0, False))
        worksheet.write("A9", "COTISATIONS", self.dis(workbook, 'left', 0, True))
        worksheet.write("B10", "TRIMESTRE", self.dis(workbook, 'left', 0, False))
        worksheet.write("B11", "ANNEE", self.dis(workbook, 'left', 0, False))
        worksheet.write("B12", "MODE DE PAIEMENT", self.dis(workbook, 'left', 0, False))
        worksheet.write("B13", "REFERENCE", self.dis(workbook, 'left', 0, False))
        worksheet.write("B14", "Taux Employeur", self.dis(workbook, 'left', 0, False))
        worksheet.write("B15", "Taux Travailleur", self.dis(workbook, 'left', 0, False))
        worksheet.write("B16", "Montant Plafonnement", self.dis(workbook, 'left', 0, False))
        worksheet.write("B17", "Montant SME", self.dis(workbook, 'left', 0, False))
        worksheet.write("A19", "MOIS CONCERNES :", self.dis(workbook, 'left', 0, True))
        worksheet.write("A22", "RECAPITULATION :", self.dis(workbook, 'left', 0, True))
        worksheet.merge_range('C3:F3', "=DNS!I3", self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('C4:F4', comp_inf['name'].upper(), self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('C5:F5', comp_inf['tel'], self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('C6:F6', comp_inf['address'], self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('C7:C7', comp_inf['email'], self.dis(workbook, 'center', 1, False))
        # style
        worksheet.set_column('B:B', 25)
        worksheet.write("C10", "4", self.dis(workbook, 'center', 1, False))
        worksheet.write("C11", y, self.dis(workbook, 'center', 1, False))
        worksheet.write("C12", "Virement", self.dis(workbook, 'center', 1, False))
        worksheet.write("C13", None, self.dis(workbook, 'center', 1, False))
        worksheet.write("C14", comp_inf['worker_rate'], self.dis(workbook, 'center', 1, False))
        worksheet.write("C15", comp_inf['employer_rate'], self.dis(workbook, 'center', 1, False))
        worksheet.write("C16", int(plf['plf_amount']), self.dis(workbook, 'center', 1, False))
        worksheet.write("C17", 2000000, self.dis(workbook, 'center', 1, False))
        worksheet.write("C22", "MOIS 1", self.dis(workbook, 'center', 1, True))
        worksheet.write("D22", "MOIS 2", self.dis(workbook, 'center', 1, True))
        worksheet.write("E22", "MOIS 3", self.dis(workbook, 'center', 1, True))
        worksheet.write("B23", "Effectif mensuel", self.dis(workbook, 'center', 1, False))
        worksheet.write("B24", u"Totaux Salaires non plafonnés", self.dis(workbook, 'center', 1, False))
        worksheet.write("B25", u"Totaux Salaires plafonnés", self.dis(workbook, 'center', 1, False))
        worksheet.write("B26", "Cotisations Employeur (A)", self.dis(workbook, 'center', 1, False))
        worksheet.write("B27", "Cotisations travailleurs (B)", self.dis(workbook, 'center', 1, False))
        # month concerned
        worksheet.write("C19", mc['m1'], self.dis(workbook, 'center', 1, False))
        worksheet.write("D19", mc['m2'], self.dis(workbook, 'center', 1, False))
        worksheet.write("E19", mc['m3'], self.dis(workbook, 'center', 1, False))
        # effectif
        worksheet.write("C23", int(eff['count_mth1']), self.dis(workbook, 'center', 1, False))
        worksheet.write("D23", int(eff['count_mth2']), self.dis(workbook, 'center', 1, False))
        worksheet.write("E23", int(eff['count_mth3']), self.dis(workbook, 'center', 1, False))
        worksheet.write("C24", "=DNS!L{}".format(row_count + 15), self.dis2(workbook, 'center', 1, False))
        worksheet.write("D24", "=DNS!M{}".format(row_count + 15), self.dis2(workbook, 'center', 1, False))
        worksheet.write("E24", "=DNS!N{}".format(row_count + 15), self.dis2(workbook, 'center', 1, False))
        # salaire plafonne
        worksheet.write("C25", plf32_['p1'], self.dis2(workbook, 'center', 1, False))
        worksheet.write("D25", plf32_['p2'], self.dis2(workbook, 'center', 1, False))
        worksheet.write("E25", plf32_['p3'], self.dis2(workbook, 'center', 1, False))
        # totaux
        worksheet.write("F23", "TOTAUX", self.dis2(workbook, 'center', 1, True))
        worksheet.write_formula("F24", "=SUM(C24:E24)", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("F25", "=SUM(C25:E25)", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("F26", "=SUM(C26:E26)", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("F27", "=SUM(C27:E27)", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("F28", "=SUM(F26:F27)", self.dis2(workbook, 'center', 1, False))
        worksheet.write("F29", None)
        worksheet.write("F30", None)
        worksheet.write_formula("F31", "=+F28+F29-F30", self.dis2(workbook, 'center', 1, True))
        # cotisation employeur
        worksheet.write_formula("C26", "=C25*5%", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("D26", "=D25*5%", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("E26", "=E25*5%", self.dis2(workbook, 'center', 1, False))
        # cotisation travailleur
        worksheet.write_formula("C27", "=C25*1%", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("D27", "=D25*1%", self.dis2(workbook, 'center', 1, False))
        worksheet.write_formula("E27", "=E25*1%", self.dis2(workbook, 'center', 1, False))
        worksheet.merge_range('B28:E28', u'Total cotisations A+B', self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('B29:E29', u'Majoration de retard 10%', self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('B30:E30', u'Trop perçu antérieur à déduire', self.dis(workbook, 'center', 1, False))
        worksheet.merge_range('B31:E31', u'COTISATIONS NET A PAYER', self.dis(workbook, 'center', 1, True))
        # total cotisation A+B
        worksheet.write_formula("F29", "", self.dis(workbook, 'center', 1, False))

    def ostie_cell(self, worksheet, row, col, field_list, i, wrap):
        for val in field_list.values():
            worksheet.write(row, col, val[i], wrap)
            row += 1

    def non_plafond(self, worksheet, row, col, row_count, wrap):
        v = 15
        for i in range(row_count):
            worksheet.write_formula(row, col, '=L{}+M{}+N{}'.format(v, v, v), wrap)
            row += 1
            v += 1

    def plafond(self, worksheet, plf, row, col, row_count, wrap):
        rw = 15
        plafond = plf['plf_amount']
        for i in range(row_count):
            worksheet.write_formula(row, col,
                                    '=IF(L{}<{},L{},{})+IF(M{}<{},M{},{})+IF(N{}<{},N{},{})'.format(rw, plafond, rw,
                                                                                                    plafond, rw,
                                                                                                    plafond, rw,
                                                                                                    plafond, rw,
                                                                                                    plafond, rw,
                                                                                                    plafond), wrap)
            rw += 1
            row += 1

    def part(self, worksheet, row, col, pat_emp, row_count, wrap):
        rw = 15
        for i in range(row_count):
            worksheet.write_formula(row, col, 'P{}*{}%'.format(rw, pat_emp), wrap)
            row += 1
            rw += 1

    def ostie_cell(self, worksheet, row, col, fieldlist, field, wrap):
        for val in fieldlist:
            worksheet.write(row, col, val[field], wrap)
            row += 1

    def line_number(self, worksheet, line, row, col, wrap):
        for i in range(line):
            worksheet.write(row, col, i, wrap)
            row += 1

    def str_(self, float):
        return str(float).replace(".", ",")
