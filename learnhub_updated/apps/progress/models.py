from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    """
    Kept as its own app/table (not bolted onto Lesson) because progress
    data grows huge (rows per user per lesson) and you may want it on a
    different DB/read-replica down the line without touching content models.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey("skills.Lesson", on_delete=models.CASCADE, related_name="progress_entries")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user} - {self.lesson} ({'done' if self.completed else 'in progress'})"
