from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
# Create your views here.
from .models import FlightData
from django.http import JsonResponse
from utils import get_round_trip, one_way

TRIPS = ('one_way', 'round_trip')

def airblue_api(request):
    trip = request.GET.get('trip') or ''.lower().strip()
    dc = request.GET.get('dc')
    ar = request.GET.get('ar')
    d_date = request.GET.get('d_date')
    a_date = request.GET.get('a_date')
    errors = []
    
    if trip not in TRIPS:
        errors.append(f'(trip) value is required and allowed values are: {TRIPS}')
    elif trip == 'one_way':
        if dc and ar and d_date:
            return JsonResponse(one_way(dc, ar, d_date))
        else:
            errors.append(f'dc(depature code), ac(arrival code) and d_date(depature date) are required for {" ".join(trip.split("_"))}.')
    else:
        if dc and ar and d_date and a_date:
            return JsonResponse(get_round_trip(dc, ar, d_date, a_date))
        else:
            errors.append(f'dc(depature code), ac(arrival code), d_date(departure date) and a_date(arrival date) are required for {" ".join(trip.split("_"))}.') 
    
    return JsonResponse({'errors': errors})