import xml.etree.ElementTree as ET

ns = {
    "podcast": "https://podcastindex.org/namespace/1.0",
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "psc": "http://podlove.org/simple-chapters",
    "atom": "http://www.w3.org/2005/Atom",
}

TEMPLATES = {
    "PODCASTS": {
        "main": "./templates/podcasts/feed_podcasts.template.xml",
        "item": "./templates/podcasts/podcasts_item.template.xml",
    },
    "ARTICLES": {
        "main": "./templates/articles/feed_articles.template.xml",
        "item": "./templates/articles/articles_item.template.xml",
    },
}


def podcasts_create_episode(i: int):
    # TODO: fill episode data
    item = ET.parse(TEMPLATES["PODCASTS"]["item"]).find("item")
    item.set("id", f"id-{i}")
    item.find("title").text = f"Episode {i}"
    item.find("itunes:title", ns).text = f"Episode {i}"
    return item


def podcasts_feed_generator(doc: ET.ElementTree):
    # TODO: query directus or db for podcasts
    for channel in doc.iter("channel"):
        channel_update_data(channel)
        for i in range(5):
            channel.append(podcasts_create_episode(i))
    return doc


def articles_create(i: int):
    # TODO: fill articles data
    item = ET.parse(TEMPLATES["ARTICLES"]["item"]).find("item")
    item.set("id", f"id-{i}")
    item.find("title").text = f"Article {i}"
    return item


def articles_feed_generator(doc: ET.ElementTree):
    # TODO: query directus or db for articles
    for channel in doc.iter("channel"):
        channel_update_data(channel)
        for i in range(5):
            channel.append(articles_create(i))
    return doc


def channel_update_data(channel: ET.Element):
    # TODO: query title
    channel.find("title").text = "Smoking Goats"
    return channel


def build_feed(template_type: str):
    selected_template = TEMPLATES[template_type]["main"]
    doc = ET.parse(selected_template)

    if template_type == "PODCASTS":
        podcasts_feed_generator(doc)
    elif template_type == "ARTICLES":
        articles_feed_generator(doc)
    else:
        raise "Not valid type"

    doc.write(
        f"./feed.{template_type}.xml",
        xml_declaration=True,
        short_empty_elements=True,
        encoding="utf-8",
    )


# TODO: add api endpoint
# build_feed("PODCASTS")
# build_feed("ARTICLES")
