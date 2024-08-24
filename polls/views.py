from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Welcome to KU-polls, you are currently "
                        "viewing all polls")
