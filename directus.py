from dotenv import load_dotenv

from os import getenv
from types import NoneType

from markdown import Markdown
from requests import get, patch, post

load_dotenv()

class Movie:
    id: str
    status: str
    sort: str | NoneType
    user_created: str
    date_created: str
    user_updated: str
    date_updated: str
    title: str
    imdb_id: str
    year: str
    released: str
    runtime: str
    genre: str
    director: str
    writer: str
    actors: str
    plot: str
    language: str
    country: str
    imdb_rating: str
    poster: str
    poster_image: str
    watched_at: list[str] | NoneType
    watched: bool
    personal_rating: str
    last_watched: str

    def __init__(self, payload: object):
        for k, v in payload.items():
            setattr(self, k, v)


AUTH_HEADER = f"Bearer {getenv('DIRECTUS_AUTH_HEADER')}"
CONTENT_TYPE = "application/json"
API_HOST = getenv("DIRECTUS_API_HOST")

API_LIST_ITEMS = f"{API_HOST}/items/movies"

HEADERS = {"Authorization": AUTH_HEADER, "Content-Type": CONTENT_TYPE}


def logger(TAG: str):
    return lambda MSG: print(f"[{TAG}] {MSG}")


def directus_get_item(item_id: str) -> Movie:
    API_ITEM = f"{API_HOST}/items/movies/{item_id}"
    rItem = get(
        url=API_ITEM,
        headers=HEADERS,
    )
    item_data = rItem.json().get("data")
    return Movie(item_data)


def directus_get_items_filter(filter: str) -> list[Movie]:
    API_ITEM = f"{API_HOST}/items/movies?filter{filter}"
    rItem = get(
        url=API_ITEM,
        headers=HEADERS,
    )
    item_data = rItem.json().get("data")
    return [Movie(p) for p in item_data]


def directus_find_item_imdb_id(imdb_id: str) -> Movie | NoneType:
    API_ITEM = f"{API_HOST}/items/movies"
    rItem = get(url=API_ITEM, headers=HEADERS, params={"search": imdb_id})
    item_data = rItem.json().get("data")
    if len(item_data) > 0:
        return Movie(item_data[0])
    return None


def directus_update_item(item_id: str, data: object) -> Movie:
    API_ITEM = f"{API_HOST}/items/movies/{item_id}"
    update_result = patch(url=API_ITEM, json=data, headers=HEADERS)
    return Movie(update_result.json())


def directus_post_item(data: object) -> Movie:
    API_ITEM = f"{API_HOST}/items/movies"
    create_r = post(url=API_ITEM, json=data, headers=HEADERS)
    return Movie(create_r.json().get("data"))


def directus_import_file(imdb_id: str, url: str) -> object:
    API_IMPORT_FILE = f"{API_HOST}/files/import"
    payload = {
        "url": url,
        "data": {
            "filename_disk": imdb_id,
            "filename_download": imdb_id,
            "title": imdb_id,
        },
    }
    r = post(url=API_IMPORT_FILE, json=payload, headers=HEADERS)
    return r.json().get("data")


def fetch_movie_details(item_id: str, rating: str = None):
    log = logger("FETCH_MOVIE")
    item_data = directus_get_item(item_id)
    imdb_id = item_data.imdb_id
    log(f"fetching {imdb_id}")
    rMovie = get(url=f"http://www.omdbapi.com/?apikey=1310878&i={imdb_id}")
    movie_data = rMovie.json()

    has_poster = movie_data.get("Poster") == "N/A" or item_data.poster is not None

    log("parsing data")
    parsed_data = {
        "status": "published",
        "title": movie_data.get("Title"),
        "year": movie_data.get("Year"),
        "rated": movie_data.get("Rated"),
        "released": movie_data.get("Released"),
        "runtime": movie_data.get("Runtime"),
        "genre": movie_data.get("Genre"),
        "director": movie_data.get("Director"),
        "writer": movie_data.get("Writer"),
        "actors": movie_data.get("Actors"),
        "plot": movie_data.get("Plot"),
        "language": movie_data.get("Language"),
        "country": movie_data.get("Country"),
        "metascore": movie_data.get("Metascore"),
        "imdb_rating": movie_data.get("imdbRating"),
        "type": movie_data.get("Type"),
    }

    if not has_poster:
        parsed_data["poster"] = movie_data.get("Poster")

    if rating is not None:
        parsed_data["personal_rating"] = rating

    log(f"updating item {imdb_id}")
    directus_update_item(item_id, parsed_data)
    log(f"updated item {imdb_id}")


def fetch_poster_image(item_id: str):
    log = logger("FETCH_POSTER")
    item_data = directus_get_item(item_id)
    if not item_data.poster_image:
        log(f"started for {item_id}")
        poster_url = item_data.poster
        imdb_id = item_data.imdb_id
        poster_file = directus_import_file(imdb_id, poster_url)
        if poster_file is not None:
            log(f"imported {imdb_id} ({poster_file.get('id')})")
            directus_update_item(item_id, {"poster_image": poster_file.get("id")})
            log(f"updated {item_id}")
        else:
            log("no poste found")
    else:
        log("no poster to update")


def create_item(imdb_id: str, rating: str, last_watched: str):
    log = logger("CREATE_ITEM")
    item = directus_find_item_imdb_id(imdb_id)
    if item is None:
        log(f"POST_ITEM {imdb_id}")
        item = directus_post_item(
            {
                "imdb_id": imdb_id,
                "personal_rating": rating,
                "watched": True,
                "watched_at": [last_watched],
            }
        )
    log(f"FETCH_DETAILS {imdb_id}")
    fetch_movie_details(item.id, rating=rating)
    log(f"FETCH_POSTER {imdb_id}")
    fetch_poster_image(item.id)


def update_last_watched(imdb_id: str):
    log = logger("UPDATE_LAST_WATCHED")
    item = directus_find_item_imdb_id(imdb_id)
    if item:
        watched_at = item.watched_at
        if watched_at is not None and len(watched_at) > 0:
            last_watched = watched_at[0]
            item_id = item.id
            log(f"UPDATE {imdb_id} LAST_WATCHED {last_watched} ")
            directus_update_item(item_id, {"last_watched": last_watched})
        else:
            log(f"{imdb_id} MISSING WATCHED_AT {watched_at}")
    else:
        log(f"NOT FOUND {imdb_id}")


def process_md(file_content: str):
    md = Markdown(extensions=["meta"])
    md.convert(file_content)
    meta_data = md.Meta
    rating = meta_data.get("personalrating")[0]
    last_watched = meta_data.get("lastwatched")[0]
    imdb_id = meta_data.get("imdbid")[0]
    return imdb_id, rating, last_watched
