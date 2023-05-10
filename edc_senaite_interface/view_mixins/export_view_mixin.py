import pandas as pd
from django.contrib import messages
from django.views.generic.base import ContextMixin
from django.forms.models import model_to_dict
from edc_base.utils import get_utcnow

from ..models import ResultExportFile


class ExportViewMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        export_type = self.request.GET.get('export', '')
        if export_type == 'csv':
            self.export_csv()
        elif export_type == 'excel':
            self.export_excel()
        return context

    def export_csv(self):
        filename = f'{self.filename}.csv'
        df = pd.DataFrame(data=self.get_export_data)
        df.to_csv(f'media/{filename}', index=False, encoding='utf-8')
        self.create_result_export_obj(filename=filename)
        messages.add_message(
            self.request, messages.INFO,
            'Results export file successfully generated')

    def export_excel(self):
        filename = f'{self.filename}.xlsx'
        df = pd.DataFrame(data=self.get_export_data)
        df.to_excel(f'media/{filename}', index=False)
        self.create_result_export_obj(filename=filename)
        messages.add_message(
            self.request, messages.INFO,
            'Results export file successfully generated')

    @property
    def get_export_data(self):
        data = []
        queryset = self.get_wrapped_queryset(self.get_queryset())
        for obj in queryset:
            record = {'participant_id': obj.participant_id, 'requisition_id': obj.requisition_id}
            values = model_to_dict(instance=obj.object, fields=self.common_fields, )
            record.update(values)
            if obj.sample_status == 'resulted':
                results = obj.object.caregiverresultvalue_set.all()
                for result in results:
                    values = model_to_dict(instance=result, fields=self.result_fields, )
                    record.update({f'{field}': '' for field in self.storage_fields})
                    record.update(values)
            else:
                values = model_to_dict(instance=obj.object, fields=self.storage_fields, )
                record.update(values.values)
                record.update({f'{field}': '' for field in self.result_fields})
            data.append(record)
        return data

    def create_result_export_obj(self, filename=''):
        ResultExportFile.objects.create(document=filename)

    @property
    def filename(self):
        model_cls = ResultExportFile
        upload_to = model_cls.document.field.upload_to

        # Check if path is func or string
        upload_to = upload_to(None, None) if callable(upload_to) else upload_to

        file_name = f'results_export_{get_utcnow().date().strftime("%Y_%m_%d")}'

        download_path = f'{upload_to}{file_name}'
        return download_path

    @property
    def result_fields(self):
        return ['analysis_title', 'analysis_keyword', 'result_value',
                'result_unit', 'date_resulted']

    @property
    def storage_fields(self):
        return ['storage_location', 'date_stored']

    @property
    def common_fields(self):
        return ['sample_id', 'sample_status', 'is_partition', 'parent_id', ]
