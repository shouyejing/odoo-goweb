{
    'name': 'Zap Theme',
    'description': 'Zap Theme - Html5 Responsive Bootstrap Theme for Odoo CMS',
    'category': 'Theme/Corporate',
    'version': '1.0',
    'author': 'Odoo SA',
    'depends': ['theme_common'],
    'data': [
        'views/assets.xml',
        'views/images_library.xml',
        'views/images_content.xml',
        'views/layout.xml',
        'views/snippets.xml',
        'views/snippets_options.xml',
        'views/customize_modal.xml',
        # STRUCTURE
        'views/snippets/s_text_image.xml',
        'views/snippets/s_image_text.xml',
        'views/snippets/s_big_message.xml',
        'views/snippets/s_text_block.xml',
        'views/snippets/s_big_picture.xml',
        # CONTENT
        'views/snippets/s_well_extended.xml',
        'views/snippets/s_quote_extended.xml',
        'views/snippets/s_panel_extended.xml',
        'views/snippets/s_separator_extended.xml',
        'views/snippets/s_share_extended.xml',
        # FEATURES
        'views/snippets/s_button.xml',
    ],
    'demo': [
        'demo/home.xml',
        'demo/layout.xml',
        'demo/blocks.xml',
        'demo/blocks_structure.xml',
        'demo/blocks_content.xml',
        'demo/blocks_features.xml',
        'demo/blocks_effects.xml',
    ],
    'images': [
        'static/description/zap_cover.gif',
    ],
    'price': 199,
    'currency': 'EUR',
    'live_test_url': 'https://theme-zap.odoo.com/page/demo_page_home'
}