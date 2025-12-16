# pages/buggy_view.py

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
    Intentionally buggy view for VS Code debugging practice.

    Bugs to find:
    (1) AttributeError when 'q' is missing (calling .strip() on None).
    (2) Logic bug: using 'is' instead of '==' when checking the sentinel 'All'.
    (3) KeyError: misspelled key 'descriptionn' in the predicate.
    """
    # ---- BUG 1: if 'q' is not provided, .strip() will raise AttributeError (NoneType has no attribute 'strip')
    query = request.GET.get('q').strip()

    field_filter = request.GET.get('field', 'All')
    projects = ALL_PROJECTS.copy()

    # ---- BUG 2: identity vs equality; 'is not "All"' can behave incorrectly; should be !=
    if field_filter is not 'All':
        projects = [p for p in projects if p['field'] == field_filter]

    # ---- BUG 3: misspelled key 'descriptionn' -> KeyError
    def predicate(p):
        return query.lower() in p['title'].lower() or query.lower() in p['descriptionn'].lower()

    if query:
        projects = list(filter(predicate, projects))

    return render(request, 'pages/buggy_search.html', {
        'projects': projects,
        'current_query': query,
        'current_field': field_filter,
    })
