from django.shortcuts import render
from django.http import HttpResponse
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Create your views here.
def index(request):
    searchQuery = request.GET.get('q', None)
    page = """
    <form method="get">
      <label for="q">Restaurant Search</label><br>
      <input type="text" id="q" name="q" ><br>
      <input type="submit" value="Submit">
    </form>"""
    if (searchQuery == None):
        return HttpResponse(page)
    searchResults = requests.post('https://places.googleapis.com/v1/places:searchText', json={
        "textQuery" : searchQuery
    }, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel',
    })
    return HttpResponse(page + "You searched for: " + searchQuery + "\nAPI: " + searchResults.text)
