from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    # On retire unique=True ici pour permettre à plusieurs personnes d'avoir l'ID
    tmdb_id = models.IntegerField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tmdb_id"], name="unique_user_movie"
            )
        ]

    def __str__(self):
        return self.title
