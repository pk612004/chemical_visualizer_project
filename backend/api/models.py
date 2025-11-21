from django.db import models
class UploadedDataset(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    csv_file = models.FileField(upload_to='uploads/')
    summary_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.uploaded_at})"
