# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ShipmentCapacity(models.Model):
    _name = 'shipment.capacity'
    _description = _('Logistics Shipment Capacity/Load')

    name = fields.Char(
        string='Name', compute='_get_name',
        store=True, readonly=False, precompute=True, translate=False)
    capacity_min = fields.Float(string='Capacity Minimum', required=True)
    capacity_max = fields.Float(string='Capacity Maximum', required=True)
    uom_id = fields.Many2one('uom.uom', string='Capacity UOM', required=True)
    description = fields.Text(string='Description', translate=True)
    
    
    @api.onchange('capacity_min', 'capacity_max')
    def _onchange_capacity(self):
        self.capacity_min = max(self.capacity_min, 0.0)
        self.capacity_max = max(self.capacity_max, 0.0)
        # avoid wrong order
        self.capacity_max = max(self.capacity_min, self.capacity_max)
    
    
    @api.depends('capacity_min', 'capacity_max', 'uom_id')
    def _get_name(self):
        for rec in self:
            rec.name = "(%s-%s) %s"%(int(max(0, rec.capacity_min)), int(max(0, rec.capacity_max)), rec.uom_id and rec.uom_id.name or '')