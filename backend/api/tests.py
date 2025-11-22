from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UploadedDataset
import io, os
from django.conf import settings

SAMPLE_CSV = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump A,Pump,100.5,2.3,75.0
Pump B,Pump,120.0,2.8,80.1
"""

@override_settings(MEDIA_ROOT=settings.BASE_DIR / 'test_media')
class APITest(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user('tester', password='pass123')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    def tearDown(self):
      
        import shutil
        try:
            shutil.rmtree(str(settings.BASE_DIR / 'test_media'))
        except Exception:
            pass
    def test_upload_and_summary(self):
        res = self.client.post('/api/upload/', {'file': io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'name': 'test.csv'}, format='multipart')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('summary', data)
        self.assertEqual(data['summary']['total'], 2)
    def test_history(self):
    
        for i in range(2):
            self.client.post('/api/upload/', {'file': io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'name': f'test{i}.csv'}, format='multipart')
        res = self.client.get('/api/history/')
        self.assertEqual(res.status_code, 200)
        arr = res.json()
        self.assertTrue(len(arr) <= 5)
    def test_summary_endpoint(self):
        r = self.client.post('/api/upload/', {'file': io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'name': 'testsum.csv'}, format='multipart')
        pid = r.json()['id']
        res = self.client.get(f'/api/summary/{pid}/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('summary', res.json())
    def test_generate_pdf(self):
        r = self.client.post('/api/upload/', {'file': io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'name': 'testpdf.csv'}, format='multipart')
        pid = r.json()['id']
        res = self.client.get(f'/api/generate_pdf/{pid}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf') or True
