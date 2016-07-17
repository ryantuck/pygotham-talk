import json
import datetime
import urllib2

import boto3
from boto3.dynamodb.types import TypeSerializer

# define list of objectively rad pokemon
rad_pokemon = [
    'Articuno', 'Moltres', 'Zapdos',
    'Mewtwo', 'Mew', 'Gyarados',
    'Rhydon', 'Alakazam', 'Gengar',
    'Charizard', 'Blastoise', 'Venusaur'
]

# function that runs on invocation
def pull_pokemon(event, context):

    # parse dates or stick to defaults
    today = datetime.datetime.utcnow().date()
    yesterday = today - datetime.timedelta(days=1)
    start_date = event.get('start', str(yesterday))
    end_date = event.get('end', str(today))

    # call an api that receives data about my pokemon
    url = 'https://api.databae.io/pokemon'
    response = urllib2.urlopen(
        url, json.dumps(
            dict(
                start=start_date,
                end=end_date
            )
        )
    )
    new_pokemon = json.loads(response.read())

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

        # weird necessary formatting for dynamoDB
        for k, v in pokemon.iteritems():
            pokemon[k] = TypeSerializer().serialize(v)

        # write record to our db
        boto3.client('dynamodb').put_item(
            TableName='my-pokemon',
            Item=pokemon,
        )

    return {
        'pokemon_loaded': len(new_pokemon),
        'load_time': str(datetime.datetime.utcnow()),
        'input_parameters': event
    }
