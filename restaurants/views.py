from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv
from django.template.loader import render_to_string

load_dotenv()
milesPerMeters = 1609.34


def getReverseGeocodedAddress(latLon):
    try:
        reverseGeocodeResult = requests.get('https://revgeocode.search.hereapi.com/v1/'
                                            + 'revgeocode'
                                            + f'?at={latLon[0]}%2C{latLon[1]}'
                                            + '&limit=1&apiKey=' + os.getenv('HERE_API_KEY'))
        reverseGeocodeResult = reverseGeocodeResult.json()
        return reverseGeocodeResult["items"][0]["title"]
    except:
        return "issues getting address"


def getPlacesSearch(query, pagetoken="", latLon=(33.77457, -84.38907), radius=5):
    searchResults = requests.post('https://places.googleapis.com/v1/places:searchText', json={
        "pageToken": pagetoken,
        "textQuery": query,
        "pageSize": 10,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": latLon[0],
                    "longitude": latLon[1],
                },
                "radius": radius * milesPerMeters,
            }
        },
        "includedType": "restaurant",
    }, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'nextPageToken,places.id,places.displayName,places.location,places.formattedAddress,places.priceLevel',
    })
    return searchResults.json()


def resturantSearch(request):
    pageToken = request.GET.get('pageToken', None)
    searchQuery = request.GET.get('q', None)
    latLon = (request.GET.get('lat', None), request.GET.get("lon", None))
    address = "Atlanta"
    if (latLon[0] != None and len(latLon[0]) > 0):
        try:
            latLon = (float(latLon[0]), float(latLon[1]))
        except:
            latLon = (33.77457, -84.38907)
        address = getReverseGeocodedAddress(latLon)
    else:
        latLon = (33.77457, -84.38907)

    radius = request.GET.get('radius', "5")
    try:
        radius = float(radius)
    except:
        radius = 5
    if (searchQuery == None):
        return render(request, 'restaurants/search.html')
    searchResults = getPlacesSearch(searchQuery, pageToken, latLon, radius)
    if (pageToken != None):
        context = {
            "query": searchQuery,
            "searchResults": searchResults,
        }
        additionalHtml = render_to_string('restaurants/searchResultsItems.html', context)
        return JsonResponse({
            "additionalHtml": additionalHtml,
            "nextPageToken": searchResults.get("nextPageToken", ""),
            "restaurants": searchResults.get("places", []),
        })
    context = {
        "query": searchQuery,
        "address": address,
        "searchResults": searchResults,
        "GOOGLE_MAPS_API_KEY": os.getenv('FRONTEND_GOOGLE_MAPS_KEY'),
    }
    return render(request, 'restaurants/search.html', context)


# based on https://developers.google.com/maps/documentation/places/web-service/place-details
def get_restaurant_details(place_id):
    detailsResult = requests.get(f'https://places.googleapis.com/v1/places/{place_id}',
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'photos,location,types,nationalPhoneNumber,formattedAddress,rating,regularOpeningHours,'
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
        'lat': details["location"]["latitude"],
        'lon': details["location"]["longitude"],
        "GOOGLE_MAPS_API_KEY": os.getenv('FRONTEND_GOOGLE_MAPS_KEY'),
        'photos': details["photos"]
    }
    return render(request, 'restaurants/detail.html', context)
