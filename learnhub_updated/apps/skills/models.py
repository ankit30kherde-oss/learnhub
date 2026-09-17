from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Skill(models.Model):
    """
    Top-level track, e.g. 'DevOps', 'Cloud', 'Security' (added later with
    zero code changes — just a new row created in /admin).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name/class")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("skill_detail", args=[self.slug])


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    cover_image = models.ImageField(upload_to="course_covers/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.slug])

    def ordered_lessons(self):
        """All lessons in this course, in the order they should be taken."""
        lessons = []
        for module in self.modules.all():
            lessons.extend(module.lessons.all())
        return lessons


class Module(models.Model):
    """A chapter/section within a course, e.g. 'CI/CD Fundamentals'."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} · {self.title}"


class Lesson(models.Model):
    """A single lesson page. Holds ordered ContentBlocks."""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["order"]
        unique_together = ("module", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "lesson_detail",
            args=[self.module.course.slug, self.id],
        )


class ContentBlock(models.Model):
    """
    Polymorphic-by-type content unit inside a lesson. This is what lets a
    lesson mix text + video + quiz + (later) an interactive lab, and lets
    you add new block types without touching Lesson/Module/Course at all.
    """
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"
    LAB = "lab"  # placeholder for future sandboxed-terminal labs
    BLOCK_TYPES = [
        (TEXT, "Text / Markdown"),
        (VIDEO, "Video"),
        (QUIZ, "Quiz"),
        (LAB, "Interactive Lab"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveIntegerField(default=0)

    # Shared/simple fields used depending on block_type:
    text_content = models.TextField(blank=True, help_text="Markdown, used when block_type=text")
    video_url = models.URLField(blank=True, help_text="Used when block_type=video")

    # Free-form structured data for anything else (quiz questions/answers,
    # lab spec, etc.) so new block types rarely need a schema migration.
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.lesson.title} [{self.block_type}] #{self.order}"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} -> {self.course}"
