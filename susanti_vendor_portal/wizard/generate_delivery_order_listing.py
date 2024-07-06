# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GenerateDeliveryListingWizard(models.Model):
    _name = 'generate.delivery.listing.wizard'
    _description = 'Fetch Delivery Lists from API'
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    journal_id = fields.Many2one(
    	comodel_name='account.journal',
        required=True,
     	string='Journal', domain="[('type','=','purchase')]")
    delivery_lines = fields.One2many(
        comodel_name='generate.delivery.line.wizard',
        inverse_name='wizard_id',
        string='Product Lines',
        required=True)
    
    
    def fetch_data_from_api(self):
        """Empty method that needs to be update"""
        return True
    
    
    def generate_delivery_listing(self):
        self.ensure_one()
        DeliveryListing = self.env['delivery.order.listing']
        Invoice = self.env['account.move']
        delivery_vals_list = []
        for rec in self.delivery_lines:
            delivery_lines = [(0, 0, {
                'product_id': rec.product_id.id,
                'product_uom_id': rec.product_uom_id.id,
                'quantity': rec.quantity,
            })]
            delivery_vals = {
                'name': rec.name,
                'delivery_vendor_id': rec.delivery_vendor_id.id,
                'shipment_from_id': rec.shipment_from_id.id,
                'shipment_to_id': rec.shipment_to_id.id,
                'delivery_date': rec.delivery_date,
                'delivery_lines': delivery_lines,
            }
            delivery_vals_list.append(delivery_vals)
        deliveries = DeliveryListing.create(delivery_vals_list)
        
        #CREATE VENDOR BILLS
        for delivery in deliveries:
            invoice_line_list = delivery.delivery_lines._prepare_account_move_line()
            invoice_vals = delivery._prepare_invoice_vals(
                invoice_line_list=[(0, 0, invoice_line_list)],
                journal_id=self.journal_id.id,
                invoice_date=fields.Date.today())
            invoice = Invoice.create(invoice_vals)
            delivery.invoice_ids = [(6,0,invoice.ids)]
        return deliveries
    
    def action_generate_delivery_listing(self):
        deliveries = self.generate_delivery_listing()
        if not deliveries:
            raise UserError(_("Unable to create delivery lists."))
        action = self.env['ir.actions.actions']._for_xml_id('susanti_vendor_portal.action_delivery_order_listing')
        if len(deliveries) > 1:
            action['domain'] = [('id', 'in', deliveries.ids)]
        elif len(deliveries) == 1:
            form_view = [(self.env.ref('susanti_vendor_portal.view_delivery_order_listing_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = deliveries.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_delivery_planning': False,
        }
        action['context'] = context
        return action
    
    

class GenerateDeliveryLineWizard(models.Model):
    _name = 'generate.delivery.line.wizard'
    _description = 'Delivery Lists'
    
    name = fields.Char(
        string='Reference',
        copy=False, index='trigram')
    delivery_vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor', required=True)
    shipment_from_id = fields.Many2one(
        comodel_name='shipment.location',
        string='Shipment from', required=True)
    shipment_to_id = fields.Many2one(
        comodel_name='shipment.location',
        string='Shipment to', required=True)
    delivery_date = fields.Date(string='Delivery Date', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', 
        string='Product')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]",
        compute="_compute_product_uom_id", store=True, readonly=False, precompute=True,
    )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float('Qty', default=0.0, digits='Product Unit of Measure', copy=False)
    wizard_id = fields.Many2one(
        comodel_name='generate.delivery.listing.wizard',
        string='Wizard')
    
    @api.depends('product_uom_id.category_id', 'product_id.uom_id.category_id','product_id.uom_id')
    def _compute_product_uom_id(self):
        for line in self:
            if not line.product_uom_id or line.product_uom_id.category_id != line.product_id.uom_id.category_id:
               line.product_uom_id = line.product_id.uom_id.id