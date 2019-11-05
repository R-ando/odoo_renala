from odoo import models

class ServiceCnaps(models.TransientModel):
    _name = "service.cnaps"
    def effectif_each_month(self, years, month):
        psql =  self.deadline = self.env.cr.execute("SELECT count(id) FROM etat_salaire  WHERE write_date::text LIKE "+month+"-"+years)
        return psql.fetchone()[0]

