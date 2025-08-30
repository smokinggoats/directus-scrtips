import argparse

from directus import import_movie

parser = argparse.ArgumentParser("simple_example")
parser.add_argument("imdb_id", help="tt\d+", type=str)
parser.add_argument("date", help="", type=str)
parser.add_argument("rating", help="", type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    import_movie(args.imdb_id, args.date, args.rating)
