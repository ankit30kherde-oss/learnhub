from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.skills.models import Course, Enrollment, Lesson, Module, Skill


class LinuxCourseGatingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        skill = Skill.objects.create(name="DevOps")
        course = Course.objects.create(
            skill=skill,
            title="Linux Fundamentals",
            summary="test",
            is_published=True,
        )
        module = Module.objects.create(course=course, title="Linux Basics", order=1)
        cls.lesson1 = Lesson.objects.create(module=module, title="Chapter 1", order=1)
        cls.lesson2 = Lesson.objects.create(module=module, title="Chapter 2", order=2)
        cls.user = get_user_model().objects.create_user(username="learner", password="StrongPass123!")
        cls.course = course

    def test_logged_out_user_can_only_open_first_lesson(self):
        response = self.client.get(reverse("lesson_detail", args=[self.course.slug, self.lesson1.id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("lesson_detail", args=[self.course.slug, self.lesson2.id]))
        self.assertRedirects(response, reverse("course_detail", args=[self.course.slug]))

    def test_logged_in_but_not_enrolled_user_still_gets_only_preview(self):
        self.client.login(username="learner", password="StrongPass123!")
        response = self.client.get(reverse("lesson_detail", args=[self.course.slug, self.lesson2.id]))
        self.assertRedirects(response, reverse("course_detail", args=[self.course.slug]))

    def test_enrolled_user_can_open_next_lesson_after_previous_completion(self):
        from apps.progress.models import LessonProgress

        Enrollment.objects.create(user=self.user, course=self.course)
        LessonProgress.objects.create(user=self.user, lesson=self.lesson1, completed=True)
        self.client.login(username="learner", password="StrongPass123!")
        response = self.client.get(reverse("lesson_detail", args=[self.course.slug, self.lesson2.id]))
        self.assertEqual(response.status_code, 200)
