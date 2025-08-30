from directus import directus_get_items_filter, update_last_watched

if __name__ == "__main__":
    for v in directus_get_items_filter("[last_watched][_nnull]")[0:2]:
        if v:
            update_last_watched(v.imdb_id)
        else:
            print(v)
