# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
    
class ShipmentLocation(models.Model):
    _name = 'vendor.pricelist.submission'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, date_end desc, name asc'
    _description = _('Vendor Pricelist Submission')
    
    name = fields.Char('Reference', required=True, default="New", tracking=True)
    date_start = fields.Date('Start Date', help="Start date for this vendor price")
    date_end = fields.Date('End Date', help="End date for this vendor price")
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('submit','Pending Review'),
            ('accepted','Accepted'),
            ('reject','Rejected'),
            ('expired','Expired'),
        ], 
        default='draft', string='Status', translate=False)
    product_supplier_info_line = fields.One2many(
        comodel_name='product.supplierinfo',
        inverse_name='vendor_submission_id',
        string='Vendor Pricelist Items'
    )
    
    
    # EXTENDS portal portal.mixin
    def _compute_access_url(self):
        super()._compute_access_url()
        for move in self:
            move.access_url = '/my/invoices/%s' % (move.id)
    