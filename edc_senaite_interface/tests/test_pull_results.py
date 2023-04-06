from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from edc_senaite_interface.classes.get_results import AnalysisResult
from ..models import SenaiteResult, SenaiteResultValue


@tag('get_results')
class TestSendMessage(TestCase):

    def setUp(self):
        host = "https://bhplims-dev.bhp.org.bw"
        user = "admin"
        password = "gah+w2Tu"
        self.client = 'TESTING'
        analysis_request = AnalysisResult(host=host)
        if analysis_request.auth(user, password):
            self.analysis_request = analysis_request
        else:
            raise ValidationError('Cannot authenticate')

    def test_pull_result_invalid(self):
        """ Test pulling result for analysis request that has not yet been resulted
            or transitioned to storage, does not create a result instance for the
            sample_id.
        """
        sample_id = '01102AAM73'
        self.analysis_request.get_sample_results(sample_id=sample_id)
        self.assertEqual(SenaiteResult.objects.filter(
            sample_id=sample_id).count(), 0)

    def test_pull_result_stored(self):
        """ Test pulling result for analysis request in storage, creates result
            instance with storage properties but no result values for analyses.
        """
        sample_id = '01131AAL7007'
        self.analysis_request.get_sample_results(sample_id)
        result_objs = SenaiteResult.objects.filter(sample_id=sample_id)
        self.assertEqual(result_objs.count(), 1)
        self.assertEqual(
            SenaiteResultValue.objects.filter(result=result_objs[0]).count(), 0)

    def test_partition_has_primary_id(self):
        """ Test pulling result for a partition of an AR, creates result
            instance and populates attributes relating the the primary/parent sample
            for the partition.
        """
        sample_id = '01131AAL7007'
        self.analysis_request.get_sample_results(sample_id)
        result_obj = SenaiteResult.objects.get(sample_id=sample_id)
        parent_id = getattr(result_obj, 'parent_id')
        is_partition = getattr(result_obj, 'is_partition')
        self.assertIsNotNone(parent_id)
        self.assertTrue(is_partition)

    def test_ar_partitions_results_pulled(self):
        """ Test pulling result for a sample with partitions, creates related result
            instances for the partitions.
        """
        sample_id = '01102AAM72'
        self.analysis_request.get_sample_results(sample_id)
        result_objs = SenaiteResult.objects.filter(parent_id=sample_id, is_partition=True)
        self.assertEqual(result_objs.count(), 5)

    def test_pull_result_resulted(self):
        """ Assert if result instance and related result items are created when
            pulling for an AR that has been published.
        """
        sample_id = '01102AAM7201'
        self.analysis_request.get_sample_results(sample_id)
        result_objs = SenaiteResult.objects.filter(sample_id=sample_id, )
        self.assertEqual(result_objs.count(), 1)
        self.assertEqual(
            SenaiteResultValue.objects.filter(result=result_objs[0]).count(), 1)
