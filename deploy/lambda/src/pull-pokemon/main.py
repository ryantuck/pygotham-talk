import json
import datetime

import dataset
import requests

# define list of objectively rad pokemon
rad_pokemon = [
    'Articuno', 'Moltres', 'Zapdos',
    'Mewtwo', 'Mew', 'Gyarados',
    'Rhydon', 'Alakazam', 'Gengar',
    'Charizard', 'Blastoise', 'Venusaur'
]

# api endpoint
url = 'https://api.databae.io/pokemon'

# connect to db
db = dataset.connect('postgres://{}:{}@{}:{}/{}'.format(
    'ryan',
    'ryanryan',
    'demo-postgres.cxpuburvh4n5.us-east-1.rds.amazonaws.com',
    '5432',
    'demo',
    )
)
table = db['my_pokemon']


# function that runs on invocation
def pull_pokemon(event, context):

    # call an api that receives data about my pokemon
    new_pokemon = requests.post(url, json.dumps(event)).json()

    for pokemon in new_pokemon:

        print pokemon.get('caught_date'), pokemon.get('name')

        # classify as rad or not
        is_rad = False
        if (
                pokemon.get('level') > 50 or
                pokemon.get('name') in rad_pokemon
            ):
            is_rad = True

        # append additional parameters
        pokemon.update({
            'load_time': str(datetime.datetime.utcnow()),
            'is_rad': is_rad,
        })

        # load to db
        table.insert(pokemon)

    return {
        'pokemon_loaded': len(new_pokemon),
        'load_time': str(datetime.datetime.utcnow()),
        'input_parameters': event
    }
