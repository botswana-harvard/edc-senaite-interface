import csv
import openpyxl
import pytz
from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin
from django.forms.models import model_to_dict
from edc_base.utils import get_utcnow

from ..models import ResultExportFile
from django.http.response import HttpResponse

tz = pytz.timezone('Africa/Gaborone')


class ExportViewMixin(ContextMixin):

    requisition_model = None

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        export_type = self.request.GET.get('export', '')
        export_pending = self.request.GET.get('export_pending', False)
        if export_pending:
            data = self.get_unlinked_samples_data
            response = self.export_csv(data)

        if export_type == 'csv':
            response = self.export_csv()
        if export_type == 'excel':
            response = self.export_excel()
        return response

    def export_csv(self, data=[]):
        filename = f'{self.filename}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        export_data = data or self.get_export_data
        if export_data:
            writer = csv.DictWriter(response, fieldnames=export_data[0].keys())

            writer.writeheader()

        for row in export_data:
            writer.writerow(row)

        return response

    def export_excel(self, data=[]):
        filename = f'{self.filename}.xlsx'

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        export_data = data or self.get_export_data
        if export_data:
            sheet.append(list(export_data[0].keys()))

        for row in export_data:
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
            record = {'participant_id': obj.participant_id,
                      'requisition_id': obj.requisition_id}
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

    @property
    def get_unlinked_samples_data(self):
        data = []
        model_cls = django_apps.get_model(self.requisition_model)
        unlinked_requisitions = model_cls.objects.filter(sample_id='')

        for requisition in unlinked_requisitions:
            drawn_dt = requisition.drawn_datetime
            drawn_dt = drawn_dt.astimezone(tz) if drawn_dt else drawn_dt

            requisition_dt = requisition.requisition_datetime
            requisition_dt = requisition_dt.astimezone(tz) if requisition_dt else requisition_dt

            visit_obj = getattr(requisition, model_cls.visit_model_attr())
            data.append({
                'subject_identifier': requisition.subject_identifier,
                'panel_name': requisition.panel.name,
                'visit_code': visit_obj.visit_code,
                'visit_code_sequence': visit_obj.visit_code_sequence,
                'requisition_identifier': requisition.requisition_identifier,
                'requisition_datetime': requisition_dt,
                'drawn_datetime': drawn_dt,
                'is_drawn': requisition.is_drawn,
                'reason_not_drawn': requisition.reason_not_drawn,
                'reason_not_drawn_other': requisition.reason_not_drawn_other,
                'specimen_type': requisition.specimen_type,
                'estimated_volume': requisition.estimated_volume,
                'priority': requisition.priority,
                'item_count': requisition.item_count,
                'item_type': requisition.item_type,
                'sample_id': requisition.sample_id,
                'exists_on_lis': requisition.exists_on_lis,
                'comments': requisition.comments})
        return data

    def create_result_export_obj(self, filename=''):
        ResultExportFile.objects.create(document=filename)

    @property
    def filename(self):
        model_cls = ResultExportFile
        upload_to = model_cls.document.field.upload_to

        # Check if path is func or string
        upload_to = upload_to(None, None) if callable(upload_to) else upload_to

        file_name = f'edc_senaite_export_{get_utcnow().date().strftime("%Y_%m_%d")}'

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
