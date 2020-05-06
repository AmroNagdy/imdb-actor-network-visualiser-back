import itertools

from bson.json_util import dumps
from flask import Flask
from flask_pymongo import PyMongo

ACTORS_KEY = 'actors'
NCONST_KEY = 'nconst'
NAME_KEY = 'primaryName'

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://ReadOnly:ReadOnly@cluster0-oboxf.mongodb.net/imdbActorNetworkVisualiserDB'
app.config['MONGO_DBNAME'] = 'movies'

mongo = PyMongo(app)
db = mongo.db
collection = mongo.db['movies']

@app.route('/api/get-network')
def get_actor_network():
    movies = collection.find()

    nconst_to_name = {}
    links = {}

    for movie in movies:
        actors = movie[ACTORS_KEY]
        
        for actor_a, actor_b in itertools.combinations(actors, 2):
            nconst_a, nconst_b = actor_a[NCONST_KEY], actor_b[NCONST_KEY]
            name_a, name_b = actor_a[NAME_KEY], actor_b[NAME_KEY]

            # Add the nconst to name mapping if not already present.
            if nconst_a not in nconst_to_name.keys():
                nconst_to_name[nconst_a] = name_a
            if nconst_b not in nconst_to_name.keys():
                nconst_to_name[nconst_b] = name_b

            # Update link between two actors.
            link = (nconst_a, nconst_b)
            if link not in links.keys():
                links[link] = 1
            else:
                links[link] += 1

    network = {
        'nodes': [ { 'id': nconst, 'name': name } for nconst, name in nconst_to_name.items() ],
        'links': [ { 'source': link[0], 'target': link[1], 'weight': weight } for link, weight in links.items() ]
    }

    return dumps(network)

app.run()