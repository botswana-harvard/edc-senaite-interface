from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class ListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    resulted = ListboardFilter(
        name='resulted',
        label='Resulted',
        lookup={'sample_status': 'resulted'})

    stored = ListboardFilter(
        name='stored',
        label='Stored',
        lookup={'sample_status': 'stored'})

    primary = ListboardFilter(
        name='primary',
        label='Primary',
        lookup={'is_partition': False})

    partition = ListboardFilter(
        name='partition',
        label='Partition',
        lookup={'is_partition': True})
