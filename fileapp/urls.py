from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("send/", views.upload_view, name="upload"),
    path("receive/", views.download_view, name="download"),
    path("cancel/<str:code>/", views.cancel_share, name="cancel"),

]
