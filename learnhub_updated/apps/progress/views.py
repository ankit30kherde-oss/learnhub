from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from apps.skills.models import Course, Enrollment, Lesson
from .models import LessonProgress


@login_required
def mark_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, "Enroll in the course before marking lessons complete.")
        return redirect("course_detail", slug=course.slug)

    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    ordered = course.ordered_lessons()
    idx = ordered.index(lesson)
    if idx + 1 < len(ordered):
        next_lesson = ordered[idx + 1]
        return redirect("lesson_detail", course_slug=course.slug, lesson_id=next_lesson.id)
    return redirect("course_detail", slug=course.slug)
