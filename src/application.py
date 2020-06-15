import itertools
import imdb_api.keys as keys
import flask_config.constants as constants
import flask_config.utils as utils

from flask_pymongo import PyMongo
from flask import Flask, request

application = Flask(__name__)
application.config['MONGO_URI'] = constants.MONGO_URI
application.config['MONGO_DBNAME'] = constants.MONGO_DBNAME
mongo = PyMongo(application)
movies_collection = mongo.db[keys.MOVIES]
actors_collection = mongo.db[keys.ACTORS]


@application.route('/', methods=['GET'])
def landing_page():
    return '<h1>The Flask REST API is up and running!</h1>'


@application.route('/api/search-actors-by-name', methods=['GET'])
def search_actors_by_name():
    name_substring = request.args.get('name')
    limit = int(request.args.get('limit', default=10))

    if not utils.string_is_valid(name_substring):
        return utils.jsonify_response_with_cors([])

    query = {
        keys.PRIMARY_NAME: {
            '$regex': f'^.*{name_substring}.*$',
            '$options': 'i'  # Case insensitive.
        }
    }

    def mappingFunction(actor):
        return {
            keys.NCONST: actor[keys.NCONST],
            keys.PRIMARY_NAME: actor[keys.PRIMARY_NAME],
            keys.BIRTH_YEAR: actor[keys.BIRTH_YEAR],
            keys.DEATH_YEAR: actor[keys.DEATH_YEAR]
        }

    actors = actors_collection.find(query).limit(limit)
    response_content = [mappingFunction(actor) for actor in actors]

    return utils.jsonify_response_with_cors(response_content)


@application.route('/api/get-network-by-nconst', methods=['GET'])
def get_network_by_nconst():
    nconst = request.args.get(keys.NCONST)

    query = {
        keys.ACTORS: nconst
    }

    movies = movies_collection.find(query)

    def extract_movie_details(movie):
        return {
            keys.TCONST: movie[keys.TCONST],
            keys.AVERAGE_RATING: movie[keys.AVERAGE_RATING],
            keys.PRIMARY_TITLE: movie[keys.PRIMARY_TITLE],
            keys.START_YEAR: movie[keys.START_YEAR]
        }

    links = {}
    for movie in movies:
        # Sort to make sure the itertools.combinations returns a consistent set of links.
        actors = sorted(movie[keys.ACTORS])
        movie_details = extract_movie_details(movie)

        for link in itertools.combinations(actors, 2):
            if link not in links:
                links[link] = {
                    'weight': 1,
                    'movies': [movie_details]
                }
            else:
                links[link]['weight'] += 1
                links[link]['movies'].append(movie_details)

    nconst_to_name = {}
    for link in links:
        for nconst in link:
            if nconst not in nconst_to_name:
                actor_details = actors_collection.find_one({keys.NCONST: nconst})

                if actor_details is not None:
                    name = actor_details[keys.PRIMARY_NAME]
                    nconst_to_name[nconst] = name

    nconsts_with_names = nconst_to_name.keys()
    networkNodes = [{'id': nconst, 'name': name} for nconst, name in nconst_to_name.items()]
    networkLinks = [{'source': link[0], 'target': link[1], 'weight': link_details['weight'], 'movies': link_details['movies']} for link, link_details in links.items() if link[0] in nconsts_with_names and link[1] in nconsts_with_names]

    actor_id_to_movie_details = {}
    for node in networkNodes:
        nconst = node['id']

        # Identify the links in the network that feature the current actor.
        links_featuring_nconst = [link for link in networkLinks if nconst in {link['source'], link['target']}]

        # FlatMap the movies within each link and remove duplicates by using a set comprehension and converting the dicts to tuples for hashing.
        movies_featuring_nconst = {tuple(movie.items()) for link in links_featuring_nconst for movie in link['movies']}

        # Convert the movies from a tuple back to dict objects.
        actor_id_to_movie_details[nconst] = sorted([dict(movie) for movie in movies_featuring_nconst], key=lambda m: m[keys.START_YEAR], reverse=True)

    network = {
        'nodes': networkNodes,
        'links': networkLinks,
        'actorIdToMovieDetailsMap': actor_id_to_movie_details
    }

    return utils.jsonify_response_with_cors(network)


if __name__ == '__main__':
    application.run()
