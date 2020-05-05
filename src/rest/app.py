from bson.json_util import dumps
from flask import Flask
from flask_pymongo import PyMongo

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
        actors = movie['actors']
        
        for i, actor in enumerate(actors):
            nconst = actor['nconst']
            name = actor['primaryName']

            if nconst not in nconst_to_name.keys():
                nconst_to_name[nconst] = name

            for other_actor in actors[i+1:]:
                other_nconst = other_actor['nconst']
                
                if nconst != other_nconst:
                    link = (nconst, other_nconst)
                    if link not in links.keys():
                        links[link] = 1
                    else:
                        links[link] += 1

    network = {
        "nodes": [ { "id": nconst } for nconst in nconst_to_name.keys() ],
        "links": [ { "source": link[0], "target": link[1], "weight": weight } for link, weight in links.items() ]
    }

    return dumps(network)

app.run()