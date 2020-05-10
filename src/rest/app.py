import itertools

from bson.json_util import dumps
from flask import Flask
from flask_pymongo import PyMongo

ACTORS_KEY = 'actors'
NCONST_KEY = 'nconst'
NAME_KEY = 'primaryName'

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://ReadOnly:ReadOnly@cluster0-oboxf.mongodb.net/imdbActorNetworkVisualiserDB'
app.config['MONGO_DBNAME'] = 'imdbActorNetworkVisualiserDB'

mongo = PyMongo(app)
movies_collection = mongo.db['movies']
actors_collection = mongo.db['actors']

@app.route('/api/get-full-network')
def get_actor_network():
    movies = movies_collection.find()

    links = {}
    for movie in movies:
        actors = movie[ACTORS_KEY]
        
        for link in itertools.combinations(actors, 2):
            if link not in links.keys():
                links[link] = 1
            else:
                links[link] += 1

    nconst_to_name = {}
    for link in links:
        for nconst in link:
            if nconst not in nconst_to_name.keys():
                actor_details = actors_collection.find_one({'nconst': nconst})

                if actor_details is not None:
                    name = actor_details[NAME_KEY]
                    nconst_to_name[nconst] = name
    available_nconsts = nconst_to_name.keys()

    network = {
        'nodes': [ { 'id': nconst, 'name': name } for nconst, name in nconst_to_name.items() ],
        'links': [ { 'source': link[0], 'target': link[1], 'weight': weight } for link, weight in links.items() if link[0] in available_nconsts and link[1] in available_nconsts ]
    }

    return dumps(network)

app.run()