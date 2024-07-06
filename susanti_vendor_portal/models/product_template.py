# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    shipment_from_id = fields.Many2one('shipment.location', 'Shipment from')
    shipment_to_id = fields.Many2one('shipment.location', 'Shipment to')
    is_delivery_product = fields.Boolean('Is Delivery Product?', default=False)