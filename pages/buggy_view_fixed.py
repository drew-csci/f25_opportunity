# pages/buggy_view_fixed.py

from django.shortcuts import render

# A small in-memory dataset (similar to company_home)
ALL_PROJECTS = [
    {'id': 1, 'title': 'AI-Powered Chatbot for Customer Service', 'field': 'Artificial Intelligence',
     'description': 'Developing a chatbot using NLP to enhance support.'},
    {'id': 2, 'title': 'Sustainable Energy Management System', 'field': 'Renewable Energy',
     'description': 'Monitor & optimize energy consumption using IoT.'},
    {'id': 3, 'title': 'Smart City Traffic Management', 'field': 'Urban Planning',
     'description': 'Alleviate traffic congestion using real-time data.'},
    {'id': 4, 'title': 'Blockchain for Supply Chain Traceability', 'field': 'Blockchain',
     'description': 'Track products from origin to consumer via DLT.'},
]

def buggy_search(request):
    """
    Fixed version of the buggy view for VS Code debugging practice.

    Bugs that were fixed:
    (1) AttributeError when 'q' is missing - Fixed by using (request.GET.get('q') or "").strip()
    (2) Logic bug: using 'is' instead of '==' - Fixed by using != for comparison
    (3) KeyError: misspelled key 'descriptionn' - Fixed to use correct key 'description'
    """
    # ---- FIX 1: Handle None by providing empty string as default
    query = (request.GET.get('q') or "").strip()

    field_filter = request.GET.get('field', 'All')
    projects = ALL_PROJECTS.copy()

    # ---- FIX 2: Use equality comparison (!=) instead of identity comparison (is not)
    if field_filter != 'All':
        projects = [p for p in projects if p['field'] == field_filter]

    # ---- FIX 3: Corrected key name from 'descriptionn' to 'description'
    def predicate(p):
        return query.lower() in p['title'].lower() or query.lower() in p['description'].lower()

    if query:
        projects = list(filter(predicate, projects))

    return render(request, 'pages/buggy_search.html', {
        'projects': projects,
        'current_query': query,
        'current_field': field_filter,
    })
