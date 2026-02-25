from django.contrib import admin
from .models import WorkExperience, Education, Skill, Achievement


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'user', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'user')
    search_fields = ('position', 'company', 'description')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'field_of_study', 'user', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'user')
    search_fields = ('degree', 'institution', 'field_of_study')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'user', 'years_of_experience')
    list_filter = ('proficiency', 'category', 'user')
    search_fields = ('name', 'category')
    ordering = ('category', 'name')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'user', 'date')
    list_filter = ('date', 'user')
    search_fields = ('title', 'organization', 'description')
    ordering = ('-date',)
    date_hierarchy = 'date'
