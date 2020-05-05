import heapq

import utils
from typing import Set, List, Dict, Tuple, Any

base_url = 'https://datasets.imdbws.com/'
title_basics = 'title.basics.tsv.gz'
title_ratings = 'title.ratings.tsv.gz'
title_principals = 'title.principals.tsv.gz'
name_basics = 'name.basics.tsv.gz'

actors_key = 'actors'

# Collect movie tconsts from title_basics.
def get_movie_tconsts() -> Set[str]:
    movie_tconsts = set()

    headings_to_index, data = utils.get_headings_and_data(base_url + title_basics)

    for row in data:
        split_row = utils.split(row)

        title_type = utils.get(split_row, headings_to_index, 'titleType')
        if title_type == 'movie':
            tconst = utils.get(split_row, headings_to_index, 'tconst')
            movie_tconsts.add(tconst)

    print(f"Successfully collected {len(movie_tconsts)} movie tconsts.")
    return movie_tconsts

# Get the tconsts for the top n films.
def get_top_n_movie_ratings_and_tconsts(movie_tconsts: Set[str], limit: int) -> List[Tuple[float, str]]:
    top_n_movie_tconsts = []

    headings_to_index, data = utils.get_headings_and_data(base_url + title_ratings)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, 'tconst')
        rating = utils.get(split_row, headings_to_index, 'averageRating', lambda x: float(x))
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
def get_basic_movie_details(rating_and_tconsts: List[Tuple[float, str]]) -> Dict[str, Any]:
    tconst_to_rating = dict([tup[::-1] for tup in rating_and_tconsts])
    basic_movie_details = {}

    headings_to_index, data = utils.get_headings_and_data(base_url + title_basics)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, 'tconst')
        if tconst in tconst_to_rating.keys():
            genres = utils.get(split_row, headings_to_index, 'genres', lambda x: x.split(','))
            basic_movie_details[tconst] = {
                'tconst': tconst,
                'averageRating': tconst_to_rating[tconst],
                'primaryTitle': utils.get(split_row, headings_to_index, 'primaryTitle'),
                'startYear': utils.get(split_row, headings_to_index, 'startYear', lambda x: int(x)),
                'isAdult': utils.get(split_row, headings_to_index, 'isAdult', lambda x: bool(int(x))),
                'runtimeMinutes': utils.get(split_row, headings_to_index, 'runtimeMinutes', lambda x: int(x)),
                'genres': genres if genres is not None else []
            }

    print(f'Successfully collected basic details for {len(basic_movie_details)} movies.')
    return basic_movie_details

# Add actor nconsts to each movie_details entry.
def update_with_actor_nconsts(movie_details: Dict[str, Any]) -> None:
    tconst_set = movie_details.keys()

    headings_to_index, data = utils.get_headings_and_data(base_url + title_principals)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, 'tconst')
        nconst = utils.get(split_row, headings_to_index, 'nconst')
        category = utils.get(split_row, headings_to_index, 'category')
        if tconst in tconst_set:
            if category in {'actor', 'actress'}:
                details = movie_details[tconst]

                if actors_key in details.keys():
                    details[actors_key].append(nconst)
                else:
                    details[actors_key] = [nconst]

    # Set any movie without any actors to have an empty list for the actors_key.
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

    headings_to_index, data = utils.get_headings_and_data(base_url + name_basics)

    for row in data:
        split_row = utils.split(row)

        nconst = utils.get(split_row, headings_to_index, 'nconst')
        if nconst in relevant_nconsts:
            nconst_to_details[nconst] = {
                'nconst': nconst,
                'primaryName': utils.get(split_row, headings_to_index, 'primaryName'),
                'birthYear': utils.get(split_row, headings_to_index, 'birthYear', lambda x: int(x)),
                'deathYear': utils.get(split_row, headings_to_index, 'deathYear', lambda x: int(x))
            }

    # Map list of nconsts in the actors_key in the movie_details to basic actor details.
    for _, details in movie_details.items():
        details[actors_key] = [nconst_to_details.get(nconst) for nconst in details[actors_key]]

    print(f'Successfully updated basic movie details with actor and actress basic details.')
