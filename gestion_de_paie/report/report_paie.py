# -*- coding: utf-8 -*-

from odoo import api, models, fields

class report_paie(models.AbstractModel):
    _name = 'report.gestion_de_paie.report_paie'

    def _get_total_by_rule_category(self, obj, code):
        payslip_line = self.env['hr.payslip.line']
        rule_cate_obj = self.env['hr.salary.rule.category']

        cate_ids = rule_cate_obj.search([('code', '=', code)])

        category_total = 0
        if cate_ids:
            payslip_lines = payslip_line.search([('slip_id', '=', obj.id),('category_id', '=', cate_ids[0].id )])
            for line in payslip_lines:
                category_total += line.total

        return category_total
    
    def _get_employe_line(self, obj, parent_line):
        
        payslip_line = self.env['hr.payslip.line']

        line_ids = payslip_line.search([('slip_id', '=', obj.id), ('salary_rule_id.parent_rule_id.id', '=', parent_line.salary_rule_id.id )])
        res = line_ids and line_ids[0] or False

        return res
    
    def _get_format(self,chiffre):
        chiffre = '{:20,.2f}'.format(chiffre)
        if (chiffre!=0):
            a=str(chiffre)
            a = a.replace(',','')
            b=a.split('.')
            c=b[0]
            d=b[1]
            e=c[::-1]
            i=0
            j=3
            f=''
            while(len(e[i:j])>0):
                if (len(e[i:j])>=3):
                    f+=e[i:j]+' '
                elif (len(e[i:j])<3):
                    f+=e[i:j]
                i+=3
                j+=3
                    
            g=f[::-1]+','+d
            return g
        else : return '0,0'

    # Congé pris et approuvé durant la même période que celle du bulletin.
    def _get_employee_request_leaves(self, employee_id, date_from_fiche, date_to_fiche):
        holidays_obj = self.env['hr.holidays'].search([('employee_id', '=', employee_id.id)])
        pris = 0
        date_from_fiche = fields.Datetime.from_string(date_from_fiche)
        date_to_fiche = fields.Datetime.from_string(date_to_fiche)            
        
        for ho in holidays_obj:
            date_from_holidays = fields.Datetime.from_string(ho.date_from)
            date_to_holidays = fields.Datetime.from_string(ho.date_to)

            if ho.type == 'remove':
                # Test if days of leaves is wholly in the current mouth
                if date_from_fiche <= date_from_holidays and date_to_fiche >= date_to_holidays:
                    pris += ho.number_of_days_temp
                # Test if date of leaves is in current month
                elif date_from_holidays <= date_to_fiche and date_to_holidays >= date_from_fiche:
                    # Set the date_from
                    if date_from_holidays <= date_from_fiche:
                        date_from_calcul = date_from_fiche
                    else:
                        date_from_calcul = date_from_holidays
                    # Set the date_to
                    if date_to_holidays <= date_to_fiche:
                        date_to_calcul = date_to_holidays
                    else:
                        date_to_calcul = date_to_fiche
                    # Calculate the number of day leaves in current month
                    pris += (date_to_calcul - date_from_calcul).days + 1
                
        return pris

    # Total de l’attribution de congé approuver de la  même période que la génération du bulletin.
    def _get_employee_allocation_leaves(self, employee_id, date_from_fiche):
        holidays_obj = self.env['hr.holidays'].search([('employee_id', '=', employee_id.id)])
        acquis = 0
        month_fiche = fields.Datetime.from_string(date_from_fiche).month
        year_fiche = fields.Datetime.from_string(date_from_fiche).year

        # Check the allocation validate in current month and year
        for ho in holidays_obj:
            if ho.type == 'add' and ho.state == 'validate' and int(ho.allocation_month) == month_fiche and ho.allocation_year == year_fiche:
                acquis += ho.number_of_days_temp
                
        return acquis


    @api.multi
    def render_html(self, docids, data=None):
        #=======================================================================
        # self.model = self.env.context.get('active_model')
        # docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        #=======================================================================
        
        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': self.env['hr.payslip'].browse(docids),
            'get_total_by_rule_category': self._get_total_by_rule_category,
            'get_employe_line': self._get_employe_line,
            'get_format': self._get_format,
            'get_employee_request_leaves': self._get_employee_request_leaves,
            'get_employee_allocation_leaves': self._get_employee_allocation_leaves,
            'data': data,
        }
        return self.env['report'].render('gestion_de_paie.report_paie', docargs)

