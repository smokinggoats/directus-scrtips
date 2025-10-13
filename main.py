from flask import Flask, abort, request
import json
from datetime import datetime
from directus import fetch_poster_image, import_movie

# create a Flask instance
app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def ping():
    # return a html format string that is rendered in the browser
    return "pong"


@app.route("/directus/import-poster", methods=["GET"])
def import_poster():
    imdb_id = request.args.get("imdb_id")
    if not imdb_id:
        return abort(400, "Missing imdb_id")
    print(imdb_id)
    fetch_poster_image(imdb_id)
    return json.dumps({"updated": {"imdb_id": imdb_id}})


@app.route("/directus/import-movie", methods=["GET"])
def get_import_movie():
    imdb_id = request.args.get("imdb_id")
    watch_date = request.args.get("date", datetime.strftime(datetime.now(), "%Y-%m-%d"))
    rating = float(request.args.get("rating", "5"))
    if not imdb_id:
        return abort(400, "Missing imdb_id")
    import_movie(imdb_id, watch_date, rating)
    return json.dumps(
        {"parsed": {"imdb_id": imdb_id, "watch_date": watch_date, "rating": rating}}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
