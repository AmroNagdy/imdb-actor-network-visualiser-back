import sys
import json
import imdb_api_lib.client as client

movies_file_name = 'movies.json'
actors_file_name = 'actors.json'

if __name__ == '__main__':
    movie_tconsts = client.get_movie_tconsts()
    movie_tconst_to_ratings = client.get_movie_tconst_to_ratings(movie_tconsts)
    movie_details = client.get_basic_movie_details(movie_tconst_to_ratings)
    client.update_with_actor_nconsts(movie_details)

    actor_details = client.get_basic_actor_details(movie_details)

    with open(movies_file_name, 'w') as output_file:
        json.dump(list(movie_details.values()), output_file)
        print(
            f'Successfully written movie details as JSON to {movies_file_name}.')

    with open(actors_file_name, 'w') as output_file:
        json.dump(actor_details, output_file)
        print(
            f'Successfully written actor details as JSON to {actors_file_name}.')
