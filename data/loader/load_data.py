import gzip
import requests
import io
import csv
import heapq

base_url = 'https://datasets.imdbws.com/'

title_basics = 'title.basics.tsv.gz'
title_ratings = 'title.ratings.tsv.gz'
title_principals = 'title.principals.tsv.gz'
name_basics = 'name.basics.tsv.gz'

output_file_name = '../actor_relationships.json'

def get_response_as_list(url, stream):
    response = requests.get(url, stream=stream)
    content = gzip.decompress(response.content)
    return content.splitlines()

# Collect movie tconsts from title_basics.
def get_movie_tconsts():
    movie_tconsts = set()
    response_list = get_response_as_list(base_url + title_basics, stream=True)
    heading_row = True

    for line in response_list:
        if heading_row:
            heading_row = False
            continue

        split_line = line.decode('utf-8').split('\t')

        title_type = split_line[1]
        if title_type == 'movie':
            movie_tconsts.add(split_line[0])

    return movie_tconsts

# Get the tconsts for the top n films.
def get_top_n_movie_ratings_and_tconsts(movie_tconsts, limit):
    top_n_movie_tconsts = []
    response_list = get_response_as_list(base_url + title_ratings, stream=True)
    heading_row = True

    for line in response_list:
        if heading_row:
            heading_row = False
            continue

        split_line = line.decode('utf-8').split('\t')

        tconst, rating = split_line[0], float(split_line[1])
        if tconst in movie_tconsts:
            if len(top_n_movie_tconsts) == limit:
                heapq.heappushpop(top_n_movie_tconsts, (rating, tconst))
            else:
                heapq.heappush(top_n_movie_tconsts, (rating, tconst))

    return top_n_movie_tconsts

def get_basic_movie_details(rating_and_tconsts):
    tconst_to_rating = dict([tup[::-1] for tup in rating_and_tconsts])
    heading_to_index = {}
    basic_movie_details = []
    response_list = get_response_as_list(base_url + title_basics, stream=True)
    heading_row = True

    for line in response_list:
        split_line = line.decode('utf-8').split('\t')

        if heading_row:
            for i, heading in enumerate(split_line):
                heading_to_index[heading] = i
            heading_row = False
            continue

        tconst = split_line[0]
        if tconst in tconst_to_rating.keys():
            basic_movie_details.append({
                'tconst': tconst,
                'averageRating': tconst_to_rating[tconst],
                'primaryTitle': split_line[heading_to_index['primaryTitle']],
                'startYear': int(split_line[heading_to_index['startYear']]),
                'isAdult': bool(int(split_line[heading_to_index['isAdult']])),
                'runtimeMinutes': int(split_line[heading_to_index['runtimeMinutes']]),
                'genres': split_line[heading_to_index['genres']].split(',')
            })

    return basic_movie_details

movie_tconsts = get_movie_tconsts()
top_n_movie_ratings_and_tconsts = get_top_n_movie_ratings_and_tconsts(movie_tconsts, 1000)
basic_movie_details = get_basic_movie_details(top_n_movie_ratings_and_tconsts)
