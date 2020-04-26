import json

from imdb_api_lib.client import *

output_file_name = 'actor_relationships.json'

if __name__ == '__main__':
    movie_tconsts = get_movie_tconsts()
    top_n_movie_ratings_and_tconsts = get_top_n_movie_ratings_and_tconsts(movie_tconsts, 1000)
    movie_details = get_basic_movie_details(top_n_movie_ratings_and_tconsts)
    update_with_actor_nconsts(movie_details)
    update_with_basic_actor_details(movie_details)

    with open(output_file_name, 'w') as output_file:
        json.dump(list(movie_details.values()), output_file)
        print(f'Successfully written movie_details as JSON to {output_file_name}.')
