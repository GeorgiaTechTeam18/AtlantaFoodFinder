from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    searchQuery = request.GET.get('q', None);
    page = """

    <form action="/" method="get">
      <label for="q">Restaurant Search</label><br>
      <input type="text" id="q" name="Restaurant Search" ><br>
      <input type="submit" value="Submit">
    </form>        """
    if (searchQuery == None):
        return HttpResponse(page)
