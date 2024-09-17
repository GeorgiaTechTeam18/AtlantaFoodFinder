from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv
from django.template.loader import render_to_string
load_dotenv()

def getPlacesSearch(query, pagetoken = ""):
    searchResults = requests.post('https://places.googleapis.com/v1/places:searchText', json={
        "pageToken": pagetoken,
        "textQuery": query,
        "pageSize": 10,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": 33.77457,
                    "longitude": -84.38907
                },
                "radius": 500.0

            }
        },
        "includedType": "restaurant",
    }, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'nextPageToken,places.id,places.displayName,places.formattedAddress,places.priceLevel',
    })
    return searchResults.json()

def index(request):
    pageToken = request.GET.get('pageToken', None)
    searchQuery = request.GET.get('q', None)
    if (searchQuery == None):
        return render(request, 'restaurants/search.html')
    if (pageToken != None):
        searchResults = getPlacesSearch(searchQuery, pageToken)
        context = {
            "query": searchQuery,
            "searchResults": searchResults,
        }
        additionalHtml = render_to_string('restaurants/searchResultsItems.html', context)
        return JsonResponse({
            "additionalHtml":additionalHtml,
            "nextPageToken":searchResults.get("nextPageToken", "")
        })
    searchResults = getPlacesSearch(searchQuery)
    context = {
        "query": searchQuery,
        "searchResults": searchResults,
    }
    return render(request, 'restaurants/search.html', context)

# based on https://developers.google.com/maps/documentation/places/web-service/place-details
def get_restaurant_details(place_id):
    detailsResult = requests.get(f'https://places.googleapis.com/v1/places/{place_id}',
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'id,displayName',
    })
    return detailsResult.json()

def restaurant_detail_view(request, place_id):
    details = get_restaurant_details(place_id)
    context = {
        'restaurant': details
    }
    return render(request, 'restaurants/detail.html', context)