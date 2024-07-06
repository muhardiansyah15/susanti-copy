# -*- coding: utf-8 -*-

from odoo import models, fields, api
class DeliverOrderListing(models.Model):
    _name = 'delivery.order.listing'
    _description = 'Delivery Listing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'delivery_date desc'
    
    name = fields.Char(
        string='Reference',
        copy=False, index='trigram')
    delivery_vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Expedisi', required=True, tracking=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer', required=True, tracking=True)
    delivery_lines = fields.One2many(
        comodel_name='delivery.order.product',
        inverse_name='delivery_id',
        string='Product Lines')
    shipment_from_id = fields.Many2one(
        comodel_name='shipment.location',
        string='Shipment from', required=True, tracking=True)
    shipment_to_id = fields.Many2one(
        comodel_name='shipment.location',
        string='Shipment to', required=True, tracking=True)
    delivery_date = fields.Date(string='Delivery Date', required=True, tracking=True)
    request_date = fields.Date(string='Request Date', required=True, tracking=True)
    delivery_planning = fields.Boolean('In Planning?', default=False, required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string='Invoices')
    note = fields.Text('Notes')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count') 
    state = fields.Selection(
        selection=[ ('draft','Draft'),('confirm','Confirm')], default='draft', string='Status')

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)
            
            
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_in_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'in_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.delivery_vendor_id.id,
                'default_invoice_origin': self.name,
            })
        action['context'] = context
        return action
    
    
    def _prepare_invoice_vals(self, **kwargs):
        self.ensure_one()
        invoice_line_list = kwargs.get('invoice_line_list', [])
        journal_id = kwargs.get('journal_id', False)
        journal = journal_id and self.env['account.journal'].sudo().browse([journal_id]) or False
        invoice_date = kwargs.get('invoice_date', False)
        return {
            'date': invoice_date,
            'invoice_date': invoice_date,
            'move_type': 'in_invoice',
            'invoice_origin': self.name,
            'partner_id': self.delivery_vendor_id.id,
            'journal_id': journal_id,
            'invoice_line_ids': invoice_line_list,
            'currency_id': journal and journal.currency_id.id or self.env.company.currency_id.id,
        }
    

class DeliverOrderProduct(models.Model):
    _name = 'delivery.order.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Delivery Product'
    
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete="cascade", 
        check_company=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", index=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]",
        compute="_compute_product_uom_id", store=True, readonly=False, precompute=True,
    )
    quantity = fields.Float('Quantity', default=0.0, digits='Product Unit of Measure', copy=False)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    delivery_id = fields.Many2one(
        comodel_name='delivery.order.listing',
        string='Delivery Planning', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    
    
    @api.depends('product_uom_id.category_id', 'product_id.uom_id.category_id','product_id.uom_id')
    def _compute_product_uom_id(self):
        for line in self:
            if not line.product_uom_id or line.product_uom_id.category_id != line.product_id.uom_id.category_id:
               line.product_uom_id = line.product_id.uom_id.id
               
               
    def _prepare_account_move_line(self, **kwargs):
        self.ensure_one()
        taxes_ids = kwargs.get('taxes_ids', [])
        label = kwargs.get('label', False)
        res = {
            'display_type': 'product',
            'name': '%s' % (label or self.product_id.description),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.quantity,
            'tax_ids': taxes_ids and [(6, 0, taxes_ids)] or [],
        }
        return res