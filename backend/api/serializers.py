from rest_framework import serializers
from .models import UploadedDataset
class UploadedDatasetSerializer(serializers.ModelSerializer):
    csv_url = serializers.SerializerMethodField()
    class Meta:
        model = UploadedDataset
        fields = ['id','name','uploaded_at','summary_json','csv_url']
    def get_csv_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        try:
            return obj.csv_file.url
        except Exception:
            return None
