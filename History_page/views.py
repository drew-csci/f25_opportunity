from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import WorkExperience, Education, Skill, Achievement


@login_required
def experiences_achievements_view(request):
    """Display user's past experiences and achievements"""
    user = request.user
    
    # Get all user data
    work_experiences = WorkExperience.objects.filter(user=user)
    education = Education.objects.filter(user=user)
    skills = Skill.objects.filter(user=user)
    achievements = Achievement.objects.filter(user=user)
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category = skill.category or 'Other'
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)
    
    context = {
        'work_experiences': work_experiences,
        'education': education,
        'skills_by_category': skills_by_category,
        'achievements': achievements,
        'total_experience_years': calculate_total_experience(work_experiences),
    }
    
    return render(request, 'pages/experiences_achievements.html', context)


def calculate_total_experience(work_experiences):
    """Calculate total years of work experience"""
    from datetime import date
    total_days = 0
    
    for exp in work_experiences:
        end = exp.end_date if exp.end_date else date.today()
        days = (end - exp.start_date).days
        total_days += days
    
    return round(total_days / 365, 1)
    