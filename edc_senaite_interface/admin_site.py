from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):

    site_header = 'EDC Senaite Interface'
    site_title = 'EDC Senaite Interface'
    index_title = 'EDC Senaite Interface'
    site_url = '/administration/'


edc_senaite_interface_admin = AdminSite(name='edc_senaite_interface_admin')
