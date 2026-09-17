from django.urls import path
from . import views

urlpatterns = [
    path("lessons/<int:lesson_id>/complete/", views.mark_complete, name="mark_complete"),
]
