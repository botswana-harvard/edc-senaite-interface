from django.test import TestCase
from datetime import datetime
from django.core.exceptions import ValidationError

from ..classes import SampleImporter
from ..models import SenaiteUser


class TestSendMessage(TestCase):

    def setUp(self):
        self.host = "https://senaite-server.bhp.org.bw/"
        self.user = "ckgathi"
        self.password = "thabo321"
    
        SenaiteUser.objects.create(
            username='ckgathi',
            contact='Coulson CTK Thabo Kgathi',
            password='thabo321')
    
        self.data = {
            "Client": "AZD1222",
            "Contact": "Coulson CTK Thabo Kgathi",
            "SampleType": "Serum",
            "DateSampled": datetime.now().strftime("%Y-%m-%d %H:%M"), # "2020-07-02 14:21:20",
            "Template": "SARS-COV-2 Serology",
            "DefaultContainerType": "Cryogenic Vial",
            # Fields specific from BHP
            "ParticipantID": "12342342333",
            "ParticipantInitials": "CK",
            "Gender": "m",
            "Visit": 2,
            "VisitCode": "screening",
            "DateOfBirth": "1978-11-03",
            "Volume": "10mL",
        }


    def test_create_sample(self):
        """
        """
        importer = SampleImporter(host=self.host)
        if importer.auth(self.user, self.password):
            importer.create_sample(data=self.data)
        else:
            raise ValidationError('Cannot authenticate')
