from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import hashlib
import hmac
import time


def make_terminal_token(user_id, lesson_id, ttl_seconds=600):
    expires = int(time.time()) + ttl_seconds
    payload = f"{user_id}:{lesson_id}:{expires}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{signature}"


from apps.progress.models import LessonProgress
from .models import Skill, Course, Lesson, Enrollment


def home(request):
    skills = Skill.objects.prefetch_related("courses").all()
    return render(request, "skills/home.html", {"skills": skills})


def skill_detail(request, slug):
    skill = get_object_or_404(Skill, slug=slug)
    courses = skill.courses.filter(is_published=True)
    return render(request, "skills/skill_detail.html", {"skill": skill, "courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    is_enrolled = (
        request.user.is_authenticated
        and Enrollment.objects.filter(user=request.user, course=course).exists()
    )

    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(
            LessonProgress.objects.filter(
                user=request.user, completed=True, lesson__module__course=course
            ).values_list("lesson_id", flat=True)
        )

    # Public users can preview only the first lesson. After signup/login,
    # enrollment is required before the remaining lessons become available.
    modules_data = []
    position = 0
    previous_done = True
    for module in course.modules.all():
        lessons_data = []
        for lesson in module.lessons.all():
            done = lesson.id in completed_ids
            is_first_lesson = position == 0
            enrolled_access = is_enrolled and previous_done
            locked = not (is_first_lesson or enrolled_access)
            lessons_data.append(
                {
                    "lesson": lesson,
                    "done": done,
                    "locked": locked,
                    "preview": is_first_lesson,
                }
            )
            previous_done = done
            position += 1
        modules_data.append({"module": module, "lessons": lessons_data})

    return render(
        request,
        "skills/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "modules_data": modules_data,
            "first_lesson": course.ordered_lessons()[0] if course.ordered_lessons() else None,
        },
    )


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"You're enrolled in {course.title}. The Linux chapters are now ready for practice.")
    return redirect("course_detail", slug=slug)


def lesson_detail(request, course_slug, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course__slug=course_slug)
    course = lesson.module.course
    ordered = course.ordered_lessons()
    idx = ordered.index(lesson)
    is_first_lesson = idx == 0
    is_enrolled = request.user.is_authenticated and Enrollment.objects.filter(
        user=request.user, course=course
    ).exists()

    # First lesson is the public preview. Everything after it requires
    # authentication + enrollment. Progression still follows lesson order.
    if not is_first_lesson and not request.user.is_authenticated:
        messages.info(request, "Create a free account to unlock the remaining Linux chapters.")
        return redirect("course_detail", slug=course_slug)

    if not is_first_lesson and not is_enrolled:
        messages.info(request, "Sign up or log in, then click Enroll to unlock this chapter.")
        return redirect("course_detail", slug=course_slug)

    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(
            LessonProgress.objects.filter(
                user=request.user, completed=True, lesson__module__course=course
            ).values_list("lesson_id", flat=True)
        )

    if is_first_lesson and idx == 0:
        pass
    elif idx > 0 and ordered[idx - 1].id not in completed_ids:
        messages.info(request, f'Complete "{ordered[idx - 1].title}" first.')
        return redirect("course_detail", slug=course_slug)

    already_completed = lesson.id in completed_ids
    next_lesson = ordered[idx + 1] if idx + 1 < len(ordered) else None
    next_url = (
        reverse("lesson_detail", args=[course_slug, next_lesson.id])
        if next_lesson
        else reverse("course_detail", args=[course_slug])
    )

    notes_blocks = lesson.blocks.exclude(block_type="lab")
    lab_block = lesson.blocks.filter(block_type="lab").first()
    can_practice = request.user.is_authenticated and is_enrolled
    terminal_token = make_terminal_token(request.user.pk, lesson.id) if can_practice else ""

    return render(
        request,
        "skills/lesson_detail.html",
        {
            "lesson": lesson,
            "course": course,
            "notes_blocks": notes_blocks,
            "lab_block": lab_block,
            "already_completed": already_completed,
            "next_url": next_url,
            "is_enrolled": is_enrolled,
            "can_practice": can_practice,
            "terminal_token": terminal_token,
            "is_preview": is_first_lesson and not is_enrolled,
        },
    )


@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    return render(request, "skills/dashboard.html", {"enrollments": enrollments})
