from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class ListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    pending = ListboardFilter(
        name='resulted',
        label='Resulted Samples',
        lookup={'sample_status': 'resulted'})

    approved = ListboardFilter(
        name='stored',
        label='Stored Samples',
        lookup={'sample_status': 'stored'})
