from django.contrib import admin
from .models import Skill, Course, Module, Lesson, ContentBlock, Enrollment


class ContentBlockInline(admin.TabularInline):
    model = ContentBlock
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "level", "is_published", "order")
    list_filter = ("skill", "level", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    inlines = [ContentBlockInline]


admin.site.register(Enrollment)
