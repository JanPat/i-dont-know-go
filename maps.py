import googlemaps

from datetime import datetime
import geopy.distance

gmaps = googlemaps.Client(key='')

def get_best_score(restaurants, restaurant_options):
    '''
    Returns the name of the restaurant with the best score.
    '''

    best_score = 99999999999
    best_restaurant = ""

    for resto in restaurants:
        if restaurant_options[resto]['score'] < best_score:
            best_score = restaurant_options[resto]['score']
            best_restaurant = restaurant_options[resto]['name']

    return best_restaurant

def filter_restaurants(max_distance, method, max_duration, min_rating, restaurant_options, location):
    '''
    Filters down restaurants by distance, duration, rating. Returns best restaurant.
    '''

    now = datetime.now()

    to_keep = []

    for restaurant in restaurant_options.keys():
        resto_dict = restaurant_options[restaurant]
        
        if resto_dict['rating'] > min_rating or resto_dict['distance_km'] < max_distance:
            to_keep.append(restaurant)

    to_keep2 = []

    for restaurant in to_keep:
        resto_dict = restaurant_options[restaurant]
        directions_results = gmaps.directions(
            (location[1], location[0]), #lat/long
            (resto_dict['location'][1], resto_dict['location'][0]),
            mode = method,
            departure_time = now
        )

        duration = directions_results[0]['legs'][0]['duration'] # value in seconds
        # add duration to score
        restaurant_options[restaurant]['score'] += float(duration['value']) / 60

        if duration['value'] < max_duration * 60:
            to_keep2.append(restaurant)

    best_option = get_best_score(to_keep2, restaurant_options)

    if best_option == "":
        best_option = get_best_score(to_keep, restaurant_options)
        if best_option == "":
            best_option = get_best_score(restaurant_options.keys(), restaurant_options)

    best_option_dict = restaurant_options[best_option]
    best_option_dict['duration_s'] = duration['value']
    best_option_dict['duration_text'] = duration['text']

    return best_option_dict

def get_directions(location, method, end_location):
    '''
    Returns dictionary of navigation instructions and locations to change the instructions at.
    '''

    now = datetime.now()
    
    directions_result = gmaps.directions(
        (location[1], location[0]), #lat/long
        (end_location[1], end_location[0]),
        mode = method,
        departure_time = now
    )

    legs = directions_result[0]['legs'][0]

    distance = legs['distance']
    duration = legs['duration']
    steps = legs['steps']

    number_of_steps = len(steps)

    all_instructions = {}

    for i in range(number_of_steps):
        steps_instructions = steps[i]['html_instructions']
        string_length = len(steps_instructions)
        for j in range(string_length):
            if steps_instructions[j] == ">" and j != string_length - 1 and steps_instructions[j+1] == "<":
                steps_instructions.replace(">","")
                steps_instructions = steps_instructions[:j+1] + " " + steps_instructions[j+1:]

        is_middle = False
        ind = 0
        to_delete = []

        for letter in steps_instructions:
            if letter == ">":
                is_middle = False
                to_delete.append(ind)
            elif is_middle:
                to_delete.append(ind)
            elif letter == "<":
                is_middle = True
                to_delete.append(ind)
            ind += 1

        list_instructions = list(steps_instructions)
        for index in sorted(to_delete, reverse=True):
            del list_instructions[index]

        string_instructions = "".join([str(elem) for elem in list_instructions])

        # Add information to all_instructions dictionary

        all_instructions[str(i)] = {
            "instructions": string_instructions,
            "start_location": steps[i]['start_location'],
            "end_location": steps[i]['end_location']
        }

    return all_instructions


def get_best_match(location, min_price, max_price, max_distance, method, max_duration, min_rating):
    '''
    Returns dictionary of best match with its name, address, location, price_level, rating, distance, and duration.
    '''

    now = datetime.now()

    # Top 20 results based on location and price level. Priority given to closer restaurants.
    searching_results = gmaps.places(
        type = "restaurant",
        location = location,
        language = "en-CAN",
        min_price = min_price,
        max_price = max_price,
        open_now = True
    )['results']

    restaurant_options = {}

    count = 0

    for restaurant in searching_results:
        name = restaurant['name']
        location_resto = restaurant['geometry']['location']
        location_tuple = (location_resto['lng'], location_resto['lat'])
        rating = restaurant['rating']
        price_level = restaurant['price_level']
        distance_km = geopy.distance.distance(location, location_tuple).km
        # Score based on distance, price level, and rating. Lowest wins. Used if multiple best options.
        score = distance_km + price_level - rating
        restaurant_options[name] = {
            "name": name,
            "address": restaurant['formatted_address'],
            "location": location_tuple,
            "price_level": price_level,
            "rating": rating,
            "distance_km": distance_km,
            "score": score
        }
    count += 1
    
    # Filter restaurant options to get best restaurant
    restaurant_selection = filter_restaurants(max_distance, method, max_duration, min_rating, dict(restaurant_options), location)

    return restaurant_selection

