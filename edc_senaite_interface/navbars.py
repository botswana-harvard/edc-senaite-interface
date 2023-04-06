from django.conf import settings
from edc_navbar import NavbarItem, site_navbars, Navbar


no_url_namespace = True if settings.APP_NAME == 'edc_senaite_interface' else False

edc_senaite_interface = Navbar(name='edc_senaite_interface')

# edc_senaite_interface.append_item(
#     NavbarItem(
#         name='senaite',
#         label='Dashboard',
#         fa_icon='fa fa-home',
#         url_name=settings.DASHBOARD_URL_NAMES.get('procurement_url')))

# procurement_dashboard.append_item(
#     NavbarItem(
#         name='purchase_order',
#         title='Purchase Order',
#         label='Purchase Order',
#         fa_icon='fa fa-list-alt',
#         url_name=settings.DASHBOARD_URL_NAMES[
#             'purchase_order_listboard_url'],
#         no_url_namespace=no_url_namespace))

edc_senaite_interface.append_item(
    NavbarItem(
        name='senaite_result',
        title='Senaite Result',
        label='Senaite Result',
        fa_icon='fa fa-flask-alt',
        url_name=settings.DASHBOARD_URL_NAMES.get('senaite_result_listboard_url'),
        no_url_namespace=no_url_namespace))

site_navbars.register(edc_senaite_interface)
