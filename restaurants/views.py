import math
from xml.etree.ElementInclude import include

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv
from django.template.loader import render_to_string
from functools import cache
from UserAuth.forms import ReviewForm
from UserAuth.models import Review, User, UserRestaurant, Restaurant

load_dotenv()
milesPerMeters = 1609.34
milesPerKM = milesPerMeters/1000
r_earth = 6378

def addMileToLonDiff(lat, miles):
    return (miles * milesPerKM) / (math.cos(lat*math.pi/180) * 69)
def addMileToLatDiff(miles):
    return miles / (69) # there are about 69 miles / degree of lat

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

@cache
def getPlacesSearch(query, pagetoken="", latLon=(33.77457, -84.38907), radius=5, includedType="restaurant", minRating=1):
    latDifference = abs(addMileToLatDiff(radius))
    lonDifference = abs(addMileToLonDiff(latLon[0], radius))
    searchResults = requests.post('https://places.googleapis.com/v1/places:searchText', json={
        "pageToken": pagetoken,
        "textQuery": query,
        "pageSize": 10,
        "locationRestriction": {
            "rectangle": {
                "low": {
                    "latitude": latLon[0]-latDifference,
                    "longitude": latLon[1]-lonDifference,
                },
                "high": {
                    "latitude": latLon[0]+latDifference,
                    "longitude": latLon[1]+lonDifference,
                }
            }
        },
    "minRating": minRating,
        "includedType": includedType,
    }, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'nextPageToken,places.rating,places.id,places.displayName,places.location,places.formattedAddress,places.priceLevel',
    })
    return searchResults.json()


def resturantSearch(request):
    pageToken = request.GET.get('pageToken', None)
    searchQuery = request.GET.get('q', None)
    latLon = (request.GET.get('lat', None), request.GET.get("lon", None))
    includedType = request.GET.get('includedType', "restaurant")
    minRating = int(request.GET.get("minRating", "1"))
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
    searchResults = getPlacesSearch(searchQuery, pageToken, latLon, radius, includedType, minRating)
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
@cache
def get_restaurant_details(place_id):
    detailsResult = requests.get(f'https://places.googleapis.com/v1/places/{place_id}',
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv('GOOGLE_API_KEY'),
        'X-Goog-FieldMask': 'photos,location,types,nationalPhoneNumber,formattedAddress,rating,regularOpeningHours,'
                            'userRatingCount,displayName,reviews,',
    })
    return detailsResult.json()

# uses a set for fast access
validCuisineTypes = {"american_restaurant", "bakery", "bar", "barbecue_restaurant", "brazilian_restaurant", "breakfast_restaurant", "brunch_restaurant", "cafe", "chinese_restaurant", "coffee_shop", "fast_food_restaurant", "french_restaurant", "greek_restaurant", "hamburger_restaurant", "ice_cream_shop", "indian_restaurant", "indonesian_restaurant", "italian_restaurant", "japanese_restaurant", "korean_restaurant", "lebanese_restaurant", "mediterranean_restaurant", "mexican_restaurant", "middle_eastern_restaurant", "pizza_restaurant", "ramen_restaurant", "sandwich_shop", "seafood_restaurant", "spanish_restaurant", "steak_house", "sushi_restaurant", "thai_restaurant", "turkish_restaurant", "vegan_restaurant", "vegetarian_restaurant", "vietnamese_restaurant"}
def isCuisine(type):
    return type in validCuisineTypes

def restaurant_detail_view(request, place_id):
    details = get_restaurant_details(place_id)
    if request.method == "POST" and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        action = request.POST.get('action')
        if action == 'add_to_favorites':
            Restaurant.objects.get_or_create(
                id=place_id,
                name=details["displayName"]['text'],
            )
            UserRestaurant.objects.get_or_create(
                user=request.user,
                restaurant= Restaurant.objects.get(id=place_id),
            )

            return JsonResponse({'success': True})

        elif action == 'remove_from_favorites':
            UserRestaurant.objects.filter(
                user=request.user,
                restaurant_id=place_id
            ).delete()
            return JsonResponse({'success': True})

        elif action == 'create_a_review' and form.is_valid():
            Restaurant.objects.get_or_create(
                id=place_id,
                name=details["displayName"]['text'],
            )
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant_id = place_id
            review.title = form.cleaned_data['title']
            review.star_rating = form.cleaned_data['rating']
            review.review_text = form.cleaned_data['text']
            review.save()
            return redirect('details', place_id=place_id)  # Redirect to prevent re-submission
    else:
        form = ReviewForm()

    reviews = Review.objects.filter(restaurant_id=place_id).select_related('user')
    previouslyFavorite = False if not request.user.is_authenticated else len(UserRestaurant.objects.filter(user=request.user).filter(restaurant=place_id)) == 1
    context = {
        'place_id': place_id,
        'form': form,
        'cuisineType': ", ".join(filter(isCuisine, details["types"])).title().replace("_", " "),
        'offersTakeaway': "meal_takeaway" in details["types"],
        'offersDelivery': "meal_delivery" in details["types"],
        'contactInformation': details["nationalPhoneNumber"],
        'address': details["formattedAddress"],
        'rating': details["rating"],
        'openingHours': details["regularOpeningHours"]['weekdayDescriptions'],
        'numRatings': details["userRatingCount"],
        'name': details["displayName"]['text'],
        'localReviews' : reviews,
        'reviews': details["reviews"],
        'lat': details["location"]["latitude"],
        'lon': details["location"]["longitude"],
        "GOOGLE_MAPS_API_KEY": os.getenv('FRONTEND_GOOGLE_MAPS_KEY'),
        'photos': details["photos"],
        'isUserAuthenticated': request.user.is_authenticated,
        'previouslyFavorite': previouslyFavorite
    }

    return render(request, 'restaurants/detail.html', context)
