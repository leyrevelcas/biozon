# -*- coding: utf-8 -*-
{
    'name': "biozon",

    'summary': "Gestión de productos, clientes, pedidos y envíos para Biozon",

    'description': """
Módulo completo de gestión para Biozon: productos, clientes, pedidos, proveedores,
envíos, API-REST y vistas personalizadas con Bootstrap.
    """,

    'author': "Leyre",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',

        # Vistas
        'views/categoria.xml',
        'views/cliente.xml',
        'views/envio.xml',
        'views/pedido.xml',
        'views/producto.xml',
        'views/proveedor.xml',
        'views/menu.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
}

