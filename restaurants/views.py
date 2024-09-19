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
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.priceLevel',
    })
    return HttpResponse(page + "You searched for: " + searchQuery + "\nAPI: " + searchResults.text)

# based on https://developers.google.com/maps/documentation/places/web-service/place-details
def get_restaurant_details(place_id):
    detailsResult = requests.get(f'https://places.googleapis.com/v1/places/{place_id}',
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'types,nationalPhoneNumber,formattedAddress,rating,regularOpeningHours,'
                            'userRatingCount,displayName,reviews,',
    })
    return detailsResult.json()

def restaurant_detail_view(request, place_id):
    details = get_restaurant_details(place_id)
    context = {
        'cuisineType': details["types"][0],
        'contactInformation': details["nationalPhoneNumber"],
        'address': details["formattedAddress"],
        'rating': details["rating"],
        'openingHours': details["regularOpeningHours"]['weekdayDescriptions'],
        'numRatings': details["userRatingCount"],
        'name': details["displayName"]['text'],
        'reviews': details["reviews"],
    }
    return render(request, 'restaurants/detail.html', context)