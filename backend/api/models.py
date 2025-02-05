from django.db import models

# Create your models here.

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Add any other fields you need

    def __str__(self):
        return self.name
