# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class DeliveryInvoiceWizard(models.TransientModel):
	_name = 'delivery.invoice.wizard'
	_description = "Create Invoice from delivery"
 
	@api.model
	def default_get(self, field_list):
		res = super(DeliveryInvoiceWizard, self).default_get(field_list)
		active_ids = self._context.get('active_ids')
		delivery = self.env['delivery.order.listing'].browse(active_ids)
		res['delivery_ids'] = [(6, 0, delivery.ids)]
		delivery_invoice_wizard_line = []
		for line in delivery.mapped('delivery_lines'):
			delivery_invoice_wizard_line.append((0, 0, {
				'product_id' : line.product_id.id,
				'name': line.product_id.description,
				'quantity': line.quantity,
				'product_uom_id': line.product_uom_id.id,
			}))
		res['delivery_invoice_wizard_line'] = delivery_invoice_wizard_line
		return res

	delivery_ids = fields.Many2many(
    	comodel_name='delivery.order.listing',
    	string='Deliveries',)
	partner_id = fields.Many2one(
    	comodel_name='res.partner',
     	string='Vendor Name',)
	journal_id = fields.Many2one(
    	comodel_name='account.journal',
     	string='Journal',)
	invoice_date = fields.Date(string='Invoice Date')
	delivery_invoice_wizard_line = fields.One2many(
    	comodel_name='delivery.invoice.wizard.line',
     	inverse_name='wizard_id',
    	string='Delivery Invoice Wizard Line',)

	def create_invoice(self):
		self.ensure_one()
		invoice_line_list = []
		invoice_line_list = [(0,0, line._get_invoice_line()) for line in self.delivery_invoice_wizard_line]
		invoice_vals = self.delivery_ids[0]._prepare_invoice_vals()
		invoice_vals.update(self.delivery_ids[0]._prepare_invoice_vals(
      			invoice_line_list=invoice_line_list, 
         		journal_id=self.journal_id.id,
				invoice_date=self.invoice_date or fields.Date.today(),
        ))
		invoice_id = self.env['account.move'].create(invoice_vals)
		self.delivery_ids.write({'invoice_ids' : [(4, invoice_id.id)],})
		return invoice_vals



class DeliveryInvoiceWizardLine(models.TransientModel):
	_name = 'delivery.invoice.wizard.line'
	_description = 'Delivery Invoice Wizard Line'

	wizard_id = fields.Many2one(
    	comodel_name='delivery.invoice.wizard',
     	string='Delivery Invoice Wizard',)
	product_id = fields.Many2one(
    	comodel_name='product.product',
     	string='Product',)
	name = fields.Char(string='Label',)
	quantity = fields.Float(string='Invoice Qty',)
	price_unit = fields.Float(string='Price Unit',)
	product_uom_id = fields.Many2one('uom.uom', string='UoM',)
	tax_ids = fields.Many2many(
    	comodel_name='account.tax', 
		string='Taxes',)

	def _get_invoice_line(self):
		return {
			'product_id' : self.product_id.id,
			'display_type': 'product',
            'name': '%s' % (self.name or self.product_id.description),
			'quantity': self.quantity,
			'price_unit': self.price_unit,
		}
