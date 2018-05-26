import ASINMatcher.Link


# wrapper methods
def url_matcher(link_string):
    if not (link_string.startswith("http://") or link_string.startswith("https://")):
        link_string = "https://" + link_string
    new_link = ASINMatcher.Link.Link(link_string)
    new_link.set_details()
    return new_link


def is_valid_link(link_string):
    new_link = url_matcher(link_string)
    return new_link.get_valid()


def get_region(link_string):
    new_link = url_matcher(link_string)
    return new_link.get_region()


def get_id(link_string):
    new_link = url_matcher(link_string)
    return new_link.get_id()


def get_id_type(link_string):
    new_link = url_matcher(link_string)
    return new_link.get_id_type()
