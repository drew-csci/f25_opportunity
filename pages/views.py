from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def welcome(request):
    return render(request, 'pages/welcome.html')

@login_required
def screen1(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen1.html', {'role': role})

@login_required
def screen2(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen2.html', {'role': role})

@login_required
def screen3(request):
    role = request.user.user_type.title() if hasattr(request.user, 'user_type') else 'User'
    return render(request, 'pages/screen3.html', {'role': role})

@login_required
def company_about(request):
    # These fields would ideally come from a CompanyProfile model linked to the User.
    # For now, using placeholder text and user's email.
    company_name = request.user.display_name if hasattr(request.user, 'display_name') else 'Company'
    mission = "Our mission is to connect talented students with impactful opportunities, fostering growth and innovation."
    problems_solved = "We help companies find the right talent quickly and efficiently, while providing students with valuable real-world experience."
    contact_email = request.user.email

    context = {
        'company_name': company_name,
        'mission': mission,
        'problems_solved': problems_solved,
        'contact_email': contact_email,
    }
    return render(request, 'pages/company_about.html', context)
