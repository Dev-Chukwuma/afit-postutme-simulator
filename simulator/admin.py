from django.contrib import admin

# Register your models here.

from .models import Profile, Question, ExamResult

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'jamb_score', 'aspiring_course', 'user']
    search_fields = ['full_name', 'user__username']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'question_text', 'correct_answer', 'order']
    list_filter = ['subject']
    search_fields = ['question_text']
    ordering = ['order']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'postutme_score', 'aggregate', 'date_taken']
    list_filter = ['date_taken']
    search_fields = ['user__username']