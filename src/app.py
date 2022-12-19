import json
import logging
import os
import json
import urllib.parse
import requests

import furl
from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from paste.translogger import TransLogger

# Searcher for Avalon Media Repository

# Add any environment variables from .env
load_dotenv('../.env')

# Get environment variables
env = {}
for key in ('AVALON_URL', 'AVALON_NO_RESULTS_LINK', 'AVALON_MODULE_LINK'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Must provide environment variable: {key}')

search_url = furl.furl(env['AVALON_URL']) / 'catalog.json'
link_url = furl.furl(env['AVALON_URL']) / 'media_objects'
no_results_link = env['AVALON_NO_RESULTS_LINK']
module_link = env['AVALON_MODULE_LINK']

debug = os.environ.get('FLASK_DEBUG')

logging.root.addHandler(logging.StreamHandler())

loggerWaitress = logging.getLogger('waitress')
logger = logging.getLogger('avalon-searcher')

if debug:
    loggerWaitress.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
else:
    loggerWaitress.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

logger.info("Starting the avalon-searcher Flask application")

endpoint = 'avalon-search'


# Start the flask app, with compression enabled
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/search')
def search():

    # Get the request parameters
    args = request.args
    if 'q' not in args or args['q'] == "":
        return {
            'endpoint': endpoint,
            'error': {
                'msg': 'q parameter is required',
            },
        }, 400
    query = args['q']

    per_page = 3
    if 'per_page' in args and args['per_page'] != "":
        per_page = args['per_page']

    page = 1
    if 'page' in args and args['page'] != "" and args['page'] != "%":
        page = int(args['page']) + 1

    # Execute the Avalon search
    params = {
        'q': query,  # query
        'per_page': per_page,  # number of results per page
        'page': page,  # starting at this page (1 is the first page)
        'search_field': 'all_fields',
        'utf8': '✓',
    }

    try:
        response = requests.get(search_url.url, params=params)
    except Exception as err:
        logger.error(f'Error submitting search url={search_url.url}, params={params}\n{err}')

        return {
            'endpoint': endpoint,
            'error': {
                'msg': f'Error submitting search',
            },
        }, 500

    if response.status_code != 200:
        logger.error(f'Received {response.status_code} when submitted {query=}')

        return {
            'endpoint': endpoint,
            'error': {
                'msg': f'Received {response.status_code} when submitted {query=}',
            },
        }, 500

    logger.debug(f'Submitted url={search_url.url}, params={params}')
    logger.debug(f'Received response {response.status_code}')
    logger.debug(response.text)

    data = json.loads(response.text)

    # Gather the search results into our response
    results = []
    response = {
        'endpoint': endpoint,
        'query': query,
        "per_page": str(per_page),
        "page": str(page),
        "total": int(data['response']['pages']['total_count']),
        "module_link": module_link.replace('{query}',
                                           urllib.parse.quote_plus(query)),
        "no_results_link": no_results_link,
        "results": results
    }

    if 'docs' in data['response']:
        for item in data['response']['docs']:
            results.append({
                'title': item['title_tesi'],
                'link': (link_url / item['id']).url,
                'description': item['summary_ssi'],
                'item_format': item['avalon_resource_type_ssim'][0],
                'extra': {
                    'collection': item['collection_ssim'][0],
                },
            })

    return response


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listens on port 5000 on all interfaces.

    # Run waitress WSGI server
    serve(TransLogger(app, setup_console_handler=True),
          host='0.0.0.0', port=5000, threads=10)
