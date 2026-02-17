from django.db import models


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title
