# -*- coding: utf-8 -*-

# MODELOS PRINCIPALES DEL MÓDULO BIOZON
# Incluye: Categoría, Producto, Proveedor, Cliente, Pedido, Envío
# + Herencia y método ORM explícito


from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re   # Módulo para validar correos con expresiones regulares


# CATEGORÍA
class Category(models.Model):
    _name = 'biozon.category'
    _description = 'Categoría de productos'

    # Campos principales
    name = fields.Char(string="Nombre")
    description = fields.Text(string="Descripción")

    # Relación 1:N con productos
    products = fields.One2many(
        comodel_name="biozon.product",
        inverse_name="category",
        string="Productos"
    )

    # Campo computado: número de productos
    product_count = fields.Integer(
        string="Número de productos",
        compute="_compute_product_count",
        store=True
    )

    @api.depends('products')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.products)




# PRODUCTO
class Product(models.Model):
    _name = 'biozon.product'
    _description = 'Producto'

    # Campos principales
    name = fields.Char(string="Nombre")
    internal_code = fields.Char(string="Código interno")
    description = fields.Text(string="Descripción")
    price = fields.Float(string="Precio")
    stock = fields.Integer(string="Stock")
    is_vegan = fields.Boolean(string="¿Es vegano?")
    category = fields.Many2one("biozon.category", string="Categoría")

    # Relación N:M con proveedores
    suppliers = fields.Many2many(
        comodel_name="biozon.supplier",
        relation="products_suppliers",
        column1="product_id",
        column2="supplier_id",
        string="Proveedores"
    )

    # Campo computado: stock bajo
    low_stock = fields.Boolean(
        string="¿Stock bajo?",
        compute="_compute_low_stock",
        store=True
    )

    image = fields.Image(string="Imagen")

    @api.depends('stock')
    def _compute_low_stock(self):
        for product in self:
            product.low_stock = product.stock is not False and product.stock < 10

   
    # CONSTRAINT: Validación del precio
    # -----------------------------------
    @api.constrains('price')
    def _check_price(self):
        for product in self:
            if product.price < 0:
                raise ValidationError("El precio no puede ser negativo.")

    
    # MÉTODO ORM EXPLÍCITO 
    # Usa search() y write()
    
    def update_low_stock_products(self):
        """
        Busca todos los productos cuyo stock es menor a 10
        y actualiza su campo low_stock a True.
        Este método demuestra el uso explícito del ORM.
        """
        low_stock_products = self.env['biozon.product'].search([('stock', '<', 10)])
        low_stock_products.write({'low_stock': True})
        return True




# PROVEEDOR

class Supplier(models.Model):
    _name = 'biozon.supplier'
    _description = 'Proveedor'

    name = fields.Char(string="Nombre")
    email = fields.Char(string="Correo electrónico")
    phone = fields.Char(string="Teléfono")
    address = fields.Char(string="Dirección")

    # Relación N:M con productos
    products = fields.Many2many(
        comodel_name="biozon.product",
        relation="products_suppliers",
        column1="supplier_id",
        column2="product_id",
        string="Productos"
    )

    # Campo computado
    product_count = fields.Integer(
        string="Número de productos",
        compute="_compute_product_count",
        store=True
    )

    @api.depends('products')
    def _compute_product_count(self):
        for supplier in self:
            supplier.product_count = len(supplier.products)



# CLIENTE
class Client(models.Model):
    _name = 'biozon.client'
    _description = 'Cliente'

    # Campos principales
    name = fields.Char(string="Nombre")
    address = fields.Char(string="Dirección")
    email = fields.Char(string="Correo electrónico")
    phone = fields.Char(string="Teléfono")

    # Relación 1:N con pedidos
    orders = fields.One2many(
        comodel_name="biozon.order",
        inverse_name="client",
        string="Pedidos"
    )

    # Campo computado
    order_count = fields.Integer(
        string="Número de pedidos",
        compute="_compute_order_count",
        store=True
    )

    @api.depends('orders')
    def _compute_order_count(self):
        for client in self:
            client.order_count = len(client.orders)

 
    # VALIDACIONES (CONSTRAINTS)
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                pattern = r"[^@]+@[^@]+\.[^@]+"
                if not re.match(pattern, record.email):
                    raise ValidationError("El correo electrónico no es válido.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone:
                if not record.phone.isdigit():
                    raise ValidationError("El teléfono solo puede contener números.")
                if len(record.phone) < 9:
                    raise ValidationError("El teléfono debe tener al menos 9 dígitos.")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name:
                raise ValidationError("El nombre no puede estar vacío.")
            if any(char.isdigit() for char in record.name):
                raise ValidationError("El nombre no puede contener números.")




# PEDIDO
class Order(models.Model):
    _name = 'biozon.order'
    _description = 'Pedido'

    # Fecha por defecto usando lambda
    date_order = fields.Datetime(
        string="Fecha del pedido",
        default=lambda self: fields.Datetime.now()
    )

    # Estado del pedido
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('shipped', 'Enviado'),
            ('cancelled', 'Cancelado')
        ],
        string="Estado",
        default='draft'
    )

    client = fields.Many2one("biozon.client", string="Cliente", ondelete="set null")

    # Relación N:M con productos
    products = fields.Many2many(
        comodel_name="biozon.product",
        relation="orders_products",
        column1="order_id",
        column2="product_id",
        string="Productos"
    )

    shipment = fields.Many2one("biozon.shipment", string="Envío")

    # Campos computados
    product_count = fields.Integer(
        string="Número de productos",
        compute="_compute_product_count",
        store=True
    )

    total_amount = fields.Float(
        string="Importe total",
        compute="_compute_total_amount",
        store=True
    )

    @api.depends('products')
    def _compute_product_count(self):
        for order in self:
            order.product_count = len(order.products)

    @api.depends('products.price')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.products.mapped('price'))




# ENVÍO
class Shipment(models.Model):
    _name = 'biozon.shipment'
    _description = 'Envío'

    date_shipped = fields.Datetime(string="Fecha de envío")

    state = fields.Selection(
        [
            ('pending', 'Pendiente'),
            ('in_transit', 'En tránsito'),
            ('delivered', 'Entregado'),
            ('cancelled', 'Cancelado')
        ],
        string="Estado",
        default='pending'
    )

    order = fields.Many2one("biozon.order", string="Pedido", ondelete="cascade")

    # Campo related: cliente del pedido
    client = fields.Many2one(
        "biozon.client",
        string="Cliente",
        related="order.client",
        readonly=True
    )




# HERENCIA DEL MODELO PRODUCTO
class ProductInherit(models.Model):
    _inherit = 'biozon.product'

    internal_code = fields.Char(string="Código interno")

