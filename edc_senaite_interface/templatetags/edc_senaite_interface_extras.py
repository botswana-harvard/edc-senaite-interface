from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('edc_senaite_interface/buttons/action_button.html')
def action_button(model_wrapper):
    action_url = ''
    subject = ''
    if model_wrapper.object.sample_status == 'resulted':
        action_url = model_wrapper.object.sample_results_file
        subject = 'View Results'
    elif model_wrapper.object.sample_status == 'stored':
        action_url = model_wrapper.object.storage_location
        subject = 'View in Storage'
    return dict(
        action_url=action_url,
        subject=subject, )


@register.inclusion_tag('edc_senaite_interface/buttons/dashboard_link.html')
def dashboard_link(model_wrapper, dashboard_url=''):
    if dashboard_url:
        dashboard_url = reverse(dashboard_url,
                                kwargs={'subject_identifier': model_wrapper.participant_id})
    return dict(
        dashboard_url=dashboard_url,
        subject_identifier=model_wrapper.participant_id, )
