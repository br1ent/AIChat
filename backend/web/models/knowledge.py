from django.db import models
from django.utils.timezone import now


class KnowledgeDocument(models.Model):
    title = models.CharField(max_length=200)
    file_type = models.CharField(max_length=20)  # txt, md, pdf
    status = models.CharField(max_length=20, default="pending")  # pending, processing, completed, failed
    chunk_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} - {self.file_type} - {self.status}"
