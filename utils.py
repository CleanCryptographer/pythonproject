import requests
import re
from datetime import datetime

id_f = 'login'
passwd = 'password'
button = 'defaultActionButton'

username = 'scraper'
password = 'mehman2023'
url = 'https://www.airblue.com/bookings/Vues/flight_selection.aspx?ajax=true&action=flightSearch'

FamilyFaresKeys = (
    'cabinName',
    'familyName',
    'familyCode',
    'familyDescription',
    # 'availableSeating',
    'fareTotal',
    'fareSinglePax',
    'fareTitle',
    # 'displayHtml',
)

FlightKeys = (
    "flightCode",
    "leavingCityCode",
    "landingCityCode",
    "leavingDateTimeISO",
    "landingDateTimeISO",
    "leavingDateTimeUTC",
    "landingDateTimeUTC",
    "leavingDate",
    "landingDate",
    "leavingTime",
    "landingTime",
    "route",
    "aircraftType",
    "XBAG",
)


# def login(driver):
#     id_field = driver.find_element_by_name(id_f)
#     pas = driver.find_element_by_name(passwd)
#     time.sleep(2)
#     id_field.send_keys(username)
#     pas.send_keys(password)
#     driver.find_element_by_id(button).click()
#     return True

def map_flight_key(k):
    mapping = dict(
        flightCode="FlightNumber",
        # FlightNumber="PA-410",
        leavingCityCode="DepartureAirport",
        landingCityCode="ArrivalAirport",
        leavingDateTimeISO="DepartureDateTimeISO",
        landingDateTimeISO="ArrivalDateTimeISO",
        leavingDateTimeUTC="DepartureDateTime",
        landingDateTimeUTC="ArrivalDateTime",
        leavingDate="DepartureDate",
        landingDate="ArrivalDate",
        leavingTime="DepartureTime",
        landingTime="ArrivalTime",
        route="StopQuantity",
        aircraftType="Equipment"
    )
    return mapping.get(k, k)


def map_flight_val(k, v):
    if k in ('leavingCityCode', 'landingCityCode',):
        return dict(LocationCode=v, content='')
    elif k == 'route' and v == 'Nonstop':
        return 0
    elif k == 'aircraftType':
        return dict(AirEquipType=v, content='')
    return v

def flight_data(fl):
    Flights = []
    for ff in fl.get("Flights", []):
        flight = {map_flight_key(k): map_flight_val(k,v) for k, v in ff.items() if k in FlightKeys}
        deptTime = datetime.strptime(ff['leavingDateTimeUTC'], "%Y-%m-%d %H:%M:%SZ")
        arrTime = datetime.strptime(ff['landingDateTimeUTC'], "%Y-%m-%d %H:%M:%SZ")
        flight['ElapsedTime'] = (arrTime-deptTime).total_seconds()/60 # in minutes                 
        Flights.append(flight)
    return dict(
        ElapsedTime=Flights[0].get('ElapsedTime') if len(Flights) else None,
        FlightSegment=Flights,
    )


def fares_data(fl):
    return [
        {k: v for k, v in ff.items() if k in FamilyFaresKeys}
        for ff in fl.get("FamilyFares", [])
    ]  # FamilyFares data type is array
    # ItinTotalFare


def refine_data(data):
    Flights = []
    for ff in data.get("Flights", []):
        flight = {map_flight_key(k): map_flight_val(k,v) for k, v in ff.items() if k in FlightKeys}
        deptTime = datetime.strptime(ff['leavingDateTimeUTC'], "%Y-%m-%d %H:%M:%SZ")
        arrTime = datetime.strptime(ff['landingDateTimeUTC'], "%Y-%m-%d %H:%M:%SZ")
        flight['ElapsedTime'] = (arrTime-deptTime).total_seconds()/60 # in minutes                 
        Flights.append(flight)
    
    FamilyFares = [{k: v for k, v in ff.items() if k in FamilyFaresKeys}
                   for ff in data.get("FamilyFares", [])]  # FamilyFares data type is array
    familyCount = data.get("familyCount", 0)  # familyCount data type is integer
    return dict(
        ElapsedTime=None,
        FlightSegment=Flights,
        
    )
    # return dict(
    #     FlightDetails=Flights[0] if len(Flights) else None,
    #     # FlightsCount=len(Flights),
    #     FamilyCount=familyCount,
    #     FamilyFares=FamilyFares,
    #     # FamilyFaresCount=len(FamilyFares),
    # )
    
def airblue_to_crt(res):
        
    pricedItinData = []
    links = []
    errors = []
    errors = [ e.get("Text") for e in res.get('flightSearch', {}).get('Conflicts', []) ]
    errors = [ e.get("Text") for e in res.get('flightSearchData', {}).get('Conflicts', []) ]
        
    if len(errors) == 0:
        result = res['flightResultsModel']['flightSelectionsData']['OriginDestinations'] or []
        directionInd = "Return" if res['flightSearchModel']['flightSearchData']['roundTrip'] == True else "One Way"
        
        for r in result:
            for srNo, flight in enumerate(r.get('FlightDates', []), 1):
                data_fl = dict(
                    SequenceNumber= re.search('trip_(.+?)_date_(.*)', flight.get('uniqueID')).group(1),
                    Id=flight.get('uniqueID'),
                    FlightDate= flight.get('flightDate'),
                    AirItinerary=dict(
                        DirectionInd=directionInd,
                        OriginDestinationOptions=dict(
                            OriginDestinationOption=[]
                        )
                    ),
                    AirItineraryPricingInfo=[],
                    # TicketingInfo={},
                    # TPA_Extensions={},
                )              
                if len(flight['FlightItineraries']):        
                    for fl in flight.get('FlightItineraries', []):
                        data_fl['AirItinerary'
                                ]['OriginDestinationOptions'
                                  ]['OriginDestinationOption'].append(flight_data(fl))
                        data_fl['AirItineraryPricingInfo'] = fares_data(fl)
                pricedItinData.append(data_fl)
    
    return dict(
        OTA_AirLowFareSearchRS=dict(
            PricedItinCount=len(pricedItinData), BrandedOneWayItinCount=0,
            SimpleOneWayItinCount=0, DepartedItinCount=0,
            SoldOutItinCount=0, AvailableItinCount=0,
            Version=1.0, Success={}, Warnings=[],
            PricedItineraries=dict(
                PricedItinerary=pricedItinData
            ),
            # TPA_Extensions=dict(
            #     AirlineOrderList=dict(
            #         AirlineOrder=[
            #             dict(
            #                 Code="PK",
            #                 SequenceNumber=1,
            #                 content=""
            #             )
            #         ]
            #     )
            # )
        ),
        Links=links,
        Errors=errors,
    )


def get_api_response(url, params):
    data = []
    errors = []
    res = requests.post(url, data=params)
    res = res.json()
    return airblue_to_crt(res)
    # errors = [ e.get("Text") for e in res.get('flightSearch', {}).get('Conflicts', []) ]
    # errors = [ e.get("Text") for e in res.get('flightSearchData', {}).get('Conflicts', []) ]
        
    # if len(errors):
    #     return dict(data=data, errors=errors)
    # else:
    #     result = res['flightResultsModel']['flightSelectionsData']['OriginDestinations'] or []
    #     for r in result:
    #         for srNo, flight in enumerate(r.get('FlightDates', []), 1):
    #             data_fl = dict(
    #                 SequenceNumber= srNo,
    #                 Id=flight.get('uniqueID'),
    #                 FlightDate= flight.get('flightDate'),
    #                 FlightItineraries= [])              
    #             if len(flight['FlightItineraries']):
    #                 for fl in flight.get('FlightItineraries', []):
    #                     data_fl['FlightItineraries'].append(refine_data(fl))
    #             data.append(data_fl)
    #     return dict(data=data, errors=errors)
    


def one_way(departure, arrival, date):
    # date format 12-12-2022
    day = date.split('-')[0]
    ym = '-'.join(date.split('-')[1:][::-1])
    parms_one_ways = {
        'SS': '', 'RT': '', 'FL': 'on', 'TT': 'OW', 'DC': departure,
        'AC': arrival, 'AM': ym, 'AD': day, 'PA': '1', 'PC': '', 'PI': '',
        'CC': '', 'CR': '', 'NS': 'true', 'PX': '', 'CD': ''
    }
    return get_api_response(url, parms_one_ways)

def get_round_trip(departure, arrival, d_date, r_date):
    d_day = d_date.split('-')[0]
    d_ym = '-'.join(d_date.split('-')[1:][::-1])

    r_day = r_date.split('-')[0]
    r_ym = '-'.join(r_date.split('-')[1:][::-1])

    params_round_trip = {'SS': '', 'RT': '', 'FL': 'on', 'TT': 'RT', 'DC': departure, 'AC': arrival,
             'AM': d_ym, 'AD': d_day, 'RM': r_ym, 'RD': r_day, 'PA': '1', 'PC': '',
             'PI': '', 'CC': '', 'CR': '', 'NS': 'true', 'PX': '', 'CD': ''}
    return get_api_response(url, params_round_trip)
