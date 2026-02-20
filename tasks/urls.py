from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="tasks/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.registerPage, name="register"),
    path("", views.index, name="list"),
    path("update_task/<str:pk>/", views.updateTask, name="update_task"),
    path("delete_task/<str:pk>/", views.deleteTask, name="delete"),
    path("import/<int:provider_id>/", views.import_from_tmdb, name="import_tmdb"),
    path("fc/login/", views.fc_login, name="fc_login"),
    path("callback/", views.fc_callback, name="fc_callback"),
]
