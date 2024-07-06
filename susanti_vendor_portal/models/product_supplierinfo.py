# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ShipmentLocation(models.Model):
    _name = 'shipment.location'
    _description = _('Shipment Location')
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')


class ProductSupplierinfo(models.Model):
    _name = 'product.supplierinfo'
    _inherit = ['product.supplierinfo', 'portal.mixin']
    
    shipment_from_id = fields.Many2one('shipment.location', 'Shipment from')
    shipment_to_id = fields.Many2one('shipment.location', 'Shipment to')
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('submit','Pending Review'),
            ('accepted','Accepted'),
            ('reject','Rejected'),
            ('expired','Expired'),
        ], 
        default='draft', string='Status', translate=False)
    shipment_capacity_id = fields.Many2one(
        comodel_name='shipment.capacity',
        string='Shipment Capacity',
    )
    fee_type = fields.Selection([
        ('per_unit', 'Fee per Unit'),
        ('range', 'Fee for Capacity Range')], 
        string='Fee Type', required=True, default='per_unit', 
        help="Select whether the fee is per unit of capacity or for a range of capacity.", translate=False)
    note = fields.Text(string='Note', translate=False)
    vendor_submission_id = fields.Many2one(
        comodel_name='vendor.pricelist.submission',
        string='Vendor Pricelist Submission'
    )
    
    
    @api.model_create_multi
    def create(self, vals_list):
        result =  super().create(vals_list)
        return result
    
    def action_reject(self):
        self.ensure_one()
        self.state = 'reject'
        return True
    
    def action_submit(self):
        self.ensure_one()
        self.state = 'submit'
        return True
