import gzip
import requests
import io
import csv
import heapq
import json

from typing import *

base_url = 'https://datasets.imdbws.com/'

title_basics = 'title.basics.tsv.gz'
title_ratings = 'title.ratings.tsv.gz'
title_principals = 'title.principals.tsv.gz'
name_basics = 'name.basics.tsv.gz'
actors_key = 'actors'

output_file_name = 'actor_relationships.json'

def get(split_line: List[str], heading_index: Dict[str, int], heading: str, type_conversion_lambda=None) -> Any:
    entry = split_line[heading_index[heading]]

    if entry == '\\N':
        return None
    elif type_conversion_lambda is not None:
        return type_conversion_lambda(entry)
    else:
        return entry

def get_response_as_list(url: str, stream: bool) -> List[str]:
    response = requests.get(url, stream=stream)
    content = gzip.decompress(response.content)
    return content.splitlines()

# Collect movie tconsts from title_basics.
def get_movie_tconsts() -> Set[str]:
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

    print(f"Successfully collected {len(movie_tconsts)} movie tconsts.")
    return movie_tconsts

# Get the tconsts for the top n films.
def get_top_n_movie_ratings_and_tconsts(movie_tconsts: Set[str], limit: int) -> Tuple[float, str]:
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
                min_rating_in_top_n_movies = top_n_movie_tconsts[0][0]
                if (min_rating_in_top_n_movies < rating):
                    heapq.heappushpop(top_n_movie_tconsts, (rating, tconst))
                else:
                    continue
            else:
                heapq.heappush(top_n_movie_tconsts, (rating, tconst))

    print(f'Successfully collected the top {limit} movie tconsts.')
    return top_n_movie_tconsts

# Collect basic movie details for the specified tconsts.
def get_basic_movie_details(rating_and_tconsts: Tuple[float, str]) -> Dict[str, Any]:
    tconst_to_rating = dict([tup[::-1] for tup in rating_and_tconsts])
    basic_movie_details = {}

    response_list = get_response_as_list(base_url + title_basics, stream=True)
    heading_row = True
    heading_index = {}

    for line in response_list:
        split_line = line.decode('utf-8').split('\t')

        if heading_row:
            for i, heading in enumerate(split_line):
                heading_index[heading] = i
            heading_row = False
            continue

        tconst = split_line[0]
        if tconst in tconst_to_rating.keys():
            basic_movie_details[tconst] = {
                'tconst': tconst,
                'averageRating': tconst_to_rating[tconst],
                'primaryTitle': get(split_line, heading_index, 'primaryTitle'),
                'startYear': get(split_line, heading_index, 'startYear', lambda x: int(x)),
                'isAdult': get(split_line, heading_index, 'isAdult', lambda x: bool(int(x))),
                'runtimeMinutes': get(split_line, heading_index, 'runtimeMinutes', lambda x: int(x)),
                'genres': get(split_line, heading_index, 'genres', lambda x: x.split(','))
            }

    print(f'Successfully collected basic details for {len(basic_movie_details)} movies.')
    return basic_movie_details

# Add actor nconsts to each movie_details entry.
def update_with_actor_nconsts(movie_details: Dict[str, Any]) -> None:
    tconst_set = movie_details.keys()

    response_list = get_response_as_list(base_url + title_principals, stream=True)
    heading_row = True
    heading_index = {}

    for line in response_list:
        split_line = line.decode('utf-8').split('\t')

        if heading_row:
            for i, heading in enumerate(split_line):
                heading_index[heading] = i
            heading_row = False
            continue

        tconst, nconst, category = split_line[heading_index['tconst']], split_line[heading_index['nconst']], split_line[heading_index['category']]
        if tconst in tconst_set:
            if category in {'actor', 'actress'}:
                details = movie_details[tconst]

                if actors_key in details.keys():
                    details[actors_key].append(nconst)
                else:
                    details[actors_key] = [nconst]

    # Set any movie with no actors to have an empty list for the actors_key.
    for tconst, details in movie_details.items():
        if not actors_key in details.keys():
            details[actors_key] = []

    print(f'Successfully updated basic movie details with actor and actress nconsts.')

# Map actor nconsts to basic actor details dictionary.
def update_with_basic_actor_details(movie_details: Dict[str, Any]) -> None:
    # Collect all relevant nconsts from movie_and_actor_details.
    relevant_nconsts = set()
    for _, details in movie_details.items():
        for nconst in details[actors_key]:
            relevant_nconsts.add(nconst)

    nconst_to_details = {}

    response_list = get_response_as_list(base_url + name_basics, stream=True)
    heading_row = True
    heading_index = {}

    for line in response_list:
        split_line = line.decode('utf-8').split('\t')

        if heading_row:
            for i, heading in enumerate(split_line):
                heading_index[heading] = i
            heading_row = False
            continue

        nconst = split_line[heading_index['nconst']]
        if nconst in relevant_nconsts:
            nconst_to_details[nconst] = {
                'nconst': nconst,
                'primaryName': get(split_line, heading_index, 'primaryName'),
                'birthYear': get(split_line, heading_index, 'birthYear', lambda x: int(x)),
                'deathYear': get(split_line, heading_index, 'deathYear', lambda x: int(x)),
            }

    # Map list of nconsts in the actors_key in the movie_details to basic actor details.
    for _, details in movie_details.items():
        details[actors_key] = [nconst_to_details.get(nconst) for nconst in details[actors_key]]

    print(f'Successfully updated basic movie details with actor and actress basic details.')

if __name__ == '__main__':
    movie_tconsts = get_movie_tconsts()
    top_n_movie_ratings_and_tconsts = get_top_n_movie_ratings_and_tconsts(movie_tconsts, 1000)
    movie_details = get_basic_movie_details(top_n_movie_ratings_and_tconsts)
    update_with_actor_nconsts(movie_details)
    update_with_basic_actor_details(movie_details)

    with open(output_file_name, 'w') as output_file:
        json.dump(list(movie_details.values()), output_file)
        print(f'Successfully written movie_details as JSON to {output_file_name}.')
