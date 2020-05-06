import sys
sys.path.append('./imdb_api_lib')
import json
import imdb_api_lib.client as client

output_file_name = 'actor_relationships.json'

if __name__ == '__main__':
    movie_tconsts = client.get_movie_tconsts()
    movie_tconst_to_ratings = client.get_movie_tconst_to_ratings(movie_tconsts)
    movie_details = client.get_basic_movie_details(movie_tconst_to_ratings)
    client.update_with_actor_nconsts(movie_details)
    client.update_with_basic_actor_details(movie_details)

    with open(output_file_name, 'w') as output_file:
        json.dump(list(movie_details.values()), output_file)
        print(f'Successfully written movie_details as JSON to {output_file_name}.')
