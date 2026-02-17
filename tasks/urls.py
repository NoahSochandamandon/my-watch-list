from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="list"),
    path("update_task/<str:pk>/", views.updateTask, name="update_task"),
    path("delete_task/<str:pk>/", views.deleteTask, name="delete"),
    path("import/<int:provider_id>/", views.import_from_tmdb, name="import_tmdb"),
]
