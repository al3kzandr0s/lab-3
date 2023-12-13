import os
import random
import datetime
from math import sin, cos, sqrt, atan2, radians, pi
import pandas as pd
import numpy as np
import csv
from tqdm import tqdm

firstnames = ["Jackson", "Hudson", "Wesley", "Everett", "Jameson", "Colton", "Greyson", "Kinsley", "Milo", "Emerson", "Harrison", "Braxton", "Dean", "Remington", "Sutton", "Edward", "Preston", "Archie", "Tanner", "Sonny", "Ryan", "Hazel", "Willow", "Ivy", "Audrey", "Autumn", "Lyla", "Piper", "Tatum", "Ember", "Hope", "Edith", "Jemma", "Marigold", "Hailee", "Heather", "Maizie", "Jenny", "Farah", "Temperance", "Breanna", "Anslie", "Daena", "Breigh", "Brinly", "Dot", "Hadly", "Huxleigh", "Averitt", "Covington", "Ruta", "Byran", "Chilton", "Erving", "Alwin", "Barnes", "Parson", "Harrington", "Keats", "Klint", "Lathen", "Daniel", "Alex", "Andy"]
lastnames = ["Adams", "Allen", "Anderson", "Armstrong", "Atkinson", "Bailey", "Baker", "Barnes", "Bell", "Brooks", "Brown", "Bufford", "Camel", "Collins", "Corbyn", "Gosling", "Cooper", "Morales", "Dixon", "Davidson", "Damon", "Edwards", "Evans", "Elliott", "Fox", "Ford", "Fierman", "Fletcher", "Grant", "Gastrell", "Green", "Hawk", "Hamilton", "Harrison", "Haggar", "Holmes", "Ipson", "Jackson", "Johnson", "Jagger", "King", "Lampson", "Lewis", "Lockwood", "Major", "Matthews", "Miller", "Moore", "Murphy", "Osborne", "Pearson", "Richardson", "Scott", "Stewart", "Simpson", "Spencer", "Taylor", "Walker", "Watson", "Webb", "White", "Young", "West", "Payne"]

coords_df = pd.read_csv("./data/postcodes.csv", usecols=["Longitude", "Latitude"], dtype=np.float32).drop_duplicates()


def get_random_coords(count):
    return coords_df.sample(count, replace=True).values.tolist()


def get_random_driver_name():
    return random.choice(firstnames) + " " + random.choice(lastnames[::2])


def get_random_client_name():
    return random.choice(firstnames) + " " + random.choice(lastnames)


def calculate_distance(lon1, lat1, lon2, lat2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return 6373.0 * c


def get_random_day_of_this_year():
    start_date = datetime.date.today().replace(day=1, month=1).toordinal()
    end_date = datetime.date.today().toordinal()
    random_day = datetime.date.fromordinal(random.randint(start_date, end_date))
    return random_day


def get_random_start_end_time(distance):
    random_day = get_random_day_of_this_year()
    random_datetime = datetime.datetime.combine(random_day, datetime.datetime.min.time())
    start_time = random_datetime - datetime.timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 60))

    delta_time = distance / 50.0 * random.uniform(0.75, 1.25)
    end_time = start_time + datetime.timedelta(hours=delta_time)

    return start_time, end_time


def get_random_cost(distance, date_time):
    hours = date_time.time().hour
    rate_coef = 1 + 0.35 *(max(cos(2 * pi * ((hours - 8) % 24) / 24), 0) + max(cos(2 * pi * ((hours - 18) % 24) / 24), 0)) # 8:00 and 18:00 peaks = +35%
    return round(3.0 + distance * (1.7 * rate_coef), 2)


def get_random_optional_rating():
    if random.uniform(0, 1.0) <= 0.25:
        return random.randint(1, 10)
    else:
        return None


def get_random_optional_driver_feedback(rating):
    if random.uniform(0, 1.0) <= 0.5 and rating != None:
        return random.choice(['Driver behaviour', 'Vehicle condition', 'Music', 'Communication'])
    else:
        return None


def get_random_optional_client_feedback(rating):
    if random.uniform(0, 1.0) <= 0.5 and rating != None:
        return random.choice(['Passenger behaviour', 'Caused damage', 'Communication'])
    else:
        return None


comment_nouns = ['driver', 'taxi driver', 'trip', 'car', 'taxi', 'service']


def get_random_optional_driver_comment(rating):
    if random.uniform(0, 1.0) <= 0.35 and rating != None:
        if rating <= 3:
            return random.choice(['Awful', 'The worst', 'Very bad']) + ' ' + random.choice(comment_nouns) + '!'
        elif rating >= 7:
            return random.choice(['Prefect', 'The best', 'Very good']) + ' ' + random.choice(comment_nouns) + '!'
        else:
            return random.choice(['Acceptable', 'Could be better, especially the', 'Not ideal, but could be worse, especially the']) + ' ' + random.choice(comment_nouns) + '.'
    else:
        return None


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


if __name__ == "__main__":
    output_file_path = './data/taxi.csv'
    file_exists = os.path.isfile(output_file_path)
    print(output_file_path + (' exists, appending data...' if file_exists else ' does not exist, creating file...'))
    with open(output_file_path, 'a' if file_exists else 'w') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='unix', quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            csvwriter.writerow([
                'driver_name',
                'client_name',
                'start_point',
                'end_point',
                'start_time',
                'end_time',
                'cost',
                'driver_rating',
                'driver_feedback',
                'driver_comment',
                'client_rating',
                'client_feedback'
                ]) # header

        rows_count = 5000000 # almost 1 GB
        for start_point_coords, end_point_coords in tqdm(pairwise(get_random_coords(2 * rows_count)), total=rows_count):
            distance = calculate_distance(*end_point_coords, *start_point_coords)

            start_time, end_time = get_random_start_end_time(distance)

            driver_rating = get_random_optional_rating()
            client_rating = get_random_optional_rating()

            csvwriter.writerow([
            get_random_driver_name(), # driver_name
            get_random_client_name(), # client_name
            { 'type': 'Point', 'coordinates': start_point_coords }, # start_point
            { 'type': 'Point', 'coordinates': end_point_coords }, # end_point
            start_time, # start_time
            end_time, # end_time
            get_random_cost(distance, start_time), # cost
            driver_rating, # driver_rating
            get_random_optional_driver_feedback(driver_rating), # driver_feedback
            get_random_optional_driver_comment(driver_rating), # driver_comment
            client_rating, # client_rating
            get_random_optional_client_feedback(client_rating), # client_feedback
            ]) # data

    print('File was filled, check', output_file_path)
