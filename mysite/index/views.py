from django.shortcuts import render
from user_zone import views
def index(request):
    # Redirecting to main page
    views.create_visit_record(request, "index/index.html")
    return render(request, "index/index.html")

