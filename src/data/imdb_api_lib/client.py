import heapq
import keys
import utils

from typing import Set, List, Dict, Tuple, Any

TITLE_BASICS = 'title.basics.tsv.gz'
TITLE_RATINGS = 'title.ratings.tsv.gz'
TITLE_PRINCIPALS = 'title.principals.tsv.gz'
NAME_BASICS = 'name.basics.tsv.gz'

# Collect movie tconsts from TITLE_BASICS.
def get_movie_tconsts() -> Set[str]:
    movie_tconsts = set()

    headings_to_index, data = utils.get_headings_and_data(TITLE_BASICS)

    for row in data:
        split_row = utils.split(row)

        title_type = utils.get(split_row, headings_to_index, keys.TITLE_TYPE)
        if title_type == 'movie':
            tconst = utils.get(split_row, headings_to_index, keys.TCONST)
            movie_tconsts.add(tconst)

    print(f"Successfully collected {len(movie_tconsts)} movie tconsts.")
    return movie_tconsts

# Get the tconsts for the top n films.
def get_movie_tconst_to_ratings(movie_tconsts: Set[str]) -> Dict[str, float]:
    movie_tconst_to_ratings = {}

    headings_to_index, data = utils.get_headings_and_data(TITLE_RATINGS)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, keys.TCONST)
        rating = utils.get(split_row, headings_to_index, keys.AVERAGE_RATING, lambda x: float(x))
        if tconst in movie_tconsts and rating is not None:
            movie_tconst_to_ratings[tconst] = rating

    print(f'Successfully mapped {len(movie_tconst_to_ratings)} movie tconsts to ratings.')
    return movie_tconst_to_ratings

# Collect basic movie details for the specified tconsts.
def get_basic_movie_details(movie_tconst_to_ratings: Dict[str, float]) -> Dict[str, Any]:
    basic_movie_details = {}

    headings_to_index, data = utils.get_headings_and_data(TITLE_BASICS)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, keys.TCONST)
        if tconst in movie_tconst_to_ratings.keys():
            genres = utils.get(split_row, headings_to_index, keys.GENRES, lambda x: x.split(','))

            basic_movie_details[tconst] = {
                keys.TCONST: tconst,
                keys.AVERAGE_RATING: movie_tconst_to_ratings[tconst],
                keys.PRIMARY_TITLE: utils.get(split_row, headings_to_index, keys.PRIMARY_TITLE),
                keys.START_YEAR: utils.get(split_row, headings_to_index, keys.START_YEAR, lambda x: int(x)),
                keys.IS_ADULT: utils.get(split_row, headings_to_index, keys.IS_ADULT, lambda x: bool(int(x))),
                keys.RUNTIME_MINUTES: utils.get(split_row, headings_to_index, keys.RUNTIME_MINUTES, lambda x: int(x)),
                keys.GENRES: genres if genres is not None else []
            }

    print(f'Successfully collected details for {len(basic_movie_details)} movies.')
    return basic_movie_details

# Add actor nconsts to each movie_details entry.
def update_with_actor_nconsts(movie_details: Dict[str, Any]) -> None:
    tconst_set = movie_details.keys()

    headings_to_index, data = utils.get_headings_and_data(TITLE_PRINCIPALS)

    for row in data:
        split_row = utils.split(row)

        tconst = utils.get(split_row, headings_to_index, keys.TCONST)
        nconst = utils.get(split_row, headings_to_index, keys.NCONST)
        category = utils.get(split_row, headings_to_index, keys.CATEGORY)
        if tconst in tconst_set:
            if category in {'actor', 'actress'}:
                details = movie_details[tconst]

                if keys.ACTORS in details.keys():
                    details[keys.ACTORS].append(nconst)
                else:
                    details[keys.ACTORS] = [nconst]

    # Set any movie without any actors to have an empty list for the keys.ACTORS.
    for tconst, details in movie_details.items():
        if not keys.ACTORS in details.keys():
            details[keys.ACTORS] = []

    print(f'Successfully updated movie details with actor and actress nconsts.')

# Map actor nconsts to basic actor details dictionary.
def get_basic_actor_details(movie_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Collect all relevant nconsts from movie_and_actor_details.
    relevant_nconsts = set()
    for details in movie_details.values():
        for nconst in details[keys.ACTORS]:
            relevant_nconsts.add(nconst)

    actor_details = []

    headings_to_index, data = utils.get_headings_and_data(NAME_BASICS)

    for row in data:
        split_row = utils.split(row)

        nconst = utils.get(split_row, headings_to_index, keys.NCONST)
        primary_name = utils.get(split_row, headings_to_index, keys.PRIMARY_NAME)
        if nconst in relevant_nconsts and primary_name is not None:
            actor_details.append({
                keys.NCONST: nconst,
                keys.PRIMARY_NAME: primary_name,
                keys.BIRTH_YEAR: utils.get(split_row, headings_to_index, keys.BIRTH_YEAR, lambda x: int(x)),
                keys.DEATH_YEAR: utils.get(split_row, headings_to_index, keys.DEATH_YEAR, lambda x: int(x))
            })

    print(f'Successfully collected {len(actor_details)} actor/actress details.')
    return actor_details
