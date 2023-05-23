import csv
import openpyxl
from django.views.generic.base import ContextMixin
from django.forms.models import model_to_dict
from edc_base.utils import get_utcnow

from ..models import ResultExportFile
from django.http.response import HttpResponse


class ExportViewMixin(ContextMixin):

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        export_type = self.request.GET.get('export', '')
        if export_type == 'csv':
            response = self.export_csv()
        if export_type == 'excel':
            response = self.export_excel()
        return response

    def export_csv(self):
        filename = f'{self.filename}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.DictWriter(response, fieldnames=self.get_export_data[0].keys())

        writer.writeheader()

        for row in self.get_export_data:
            writer.writerow(row)

        return response

    def export_excel(self):
        filename = f'{self.filename}.xlsx'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(list(self.get_export_data[0].keys()))

        for row in self.get_export_data:
            sheet.append(list(row.values()))

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        workbook.save(response)

        return response

    @property
    def get_export_data(self):
        data = []
        queryset = self.get_wrapped_queryset(self.get_queryset())
        for obj in queryset:
            record = {'participant_id': obj.participant_id, 'requisition_id': obj.requisition_id}
            values = model_to_dict(instance=obj.object, fields=self.common_fields, )
            record.update(values)
            if obj.sample_status == 'resulted':
                results = getattr(obj, 'results_objs', {})
                for result in results:
                    values = model_to_dict(instance=result, fields=self.result_fields, )
                    record.update({f'{field}': '' for field in self.storage_fields})
                    record.update(values)
            else:
                values = model_to_dict(instance=obj.object, fields=self.storage_fields, )
                record.update(values)
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

        download_path = f'{file_name}'
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
