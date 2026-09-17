from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("skills/<slug:slug>/", views.skill_detail, name="skill_detail"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("courses/<slug:slug>/enroll/", views.enroll, name="enroll"),
    path("courses/<slug:course_slug>/lessons/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),
]
