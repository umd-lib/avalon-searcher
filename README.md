# avalon-searcher

Python 3 Flask application to search Avalon; provides a backend searcher to a Bento Box style search
which expects a REST interface following the Quick Search model.

## Requires

* Python 3

## Running the Webapp

```bash
# create a .env file (then manually update environment variables)
$ cp .env-template .env
```

### Running locally

```bash
# install requirements
$ pip install -r requirements.txt

# run the app with Flask
$ flask run
```

### Running in Docker

```bash
$ docker build -t avalon-searcher .
$ docker run -it --rm -p 5000:5000 --env-file=.env --read-only avalon-searcher
```

### Endpoints

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/search endpoint: `http://localhost:5000/search?q={query}&page={page number?}&per_page={results per page?}`

Example:

```bash
curl 'http://localhost:5000/search?q=henson&per_page=3&page=0'
{
  "endpoint": "avalon-search",
  "module_link": "https://av.lib.umd.edu/catalog?q=henson&search_field=all_fields&utf8=%E2%9C%93",
  "no_results_link": "https://av.lib.umd.edu/catalog",
  "page": "1",
  "per_page": "3",
  "query": "henson",
  "results": [
    {
      "description": "This special celebrates the life and career of Jim Henson following his death in 1990. The retrospective includes appearances by celebrity guests, a variety of clips from Henson's television and film work, and candid, behind-the-scenes footage of Henson working with his creative team.",
      "item_format": "Moving Image",
      "link": "https://av.lib.umd.edu/media_objects/0g354f388",
      "title": "The Muppets celebrate Jim Henson"
    },
    {
      "description": "Documentary television program on the life, work, and success of Jim Henson and his Muppets. Combines clips and interviews with Jim Henson, Jane Henson, Frank Oz, and others to present the story of the Muppets from the early days of public access television to the success of Sesame Street to international phenomenon.",
      "item_format": "Moving Image",
      "link": "https://av.lib.umd.edu/media_objects/1831ck18w",
      "title": "Henson's place: the man behind the Muppets"
    },
    {
      "description": "The Storyteller recalls a time when he was unable to think of a story to tell even though his life depended on it.",
      "item_format": "Moving Image",
      "link": "https://av.lib.umd.edu/media_objects/v979v3150",
      "title": "Jim Henson’s the storyteller: A story short"
    }
  ],
  "total": 68
}
```

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.0.x/quickstart/#debug-mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
