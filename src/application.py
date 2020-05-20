import itertools
import imdb_api.keys as keys
import flask_config.constants as constants

from flask_pymongo import PyMongo
from flask import Flask, request, jsonify

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

    if name_substring is None or name_substring == '':
        return jsonify([])

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
    response = jsonify([mappingFunction(actor) for actor in actors])
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@application.route('/api/get-network-by-nconst', methods=['GET'])
def get_network_by_nconst():
    nconst = request.args.get(keys.NCONST)

    query = {
        keys.ACTORS: nconst
    }

    movies = movies_collection.find(query)

    links = {}
    for movie in movies:
        actors = sorted(movie[keys.ACTORS])  # Sort to make sure the itertools.combinations returns the correct set of links.

        for link in itertools.combinations(actors, 2):
            if link not in links:
                links[link] = 1
            else:
                links[link] += 1

    nconst_to_name = {}
    for link in links:
        for nconst in link:
            if nconst not in nconst_to_name:
                actor_details = actors_collection.find_one({keys.NCONST: nconst})

                if actor_details is not None:
                    name = actor_details[keys.PRIMARY_NAME]
                    nconst_to_name[nconst] = name
    available_nconsts = nconst_to_name.keys()

    network = {
        'nodes': [{'id': nconst, 'name': name} for nconst, name in nconst_to_name.items()],
        'links': [{'source': link[0], 'target': link[1], 'weight': weight} for link, weight in links.items() if link[0] in available_nconsts and link[1] in available_nconsts]
    }
    response = jsonify(network)
    response..headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    application.run()
