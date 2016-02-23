import os

def get_tokens(servicemap, split_func):
    token_map = dict()
    with open(servicemap, 'r') as smap:
        for line in smap:
            tok1, tok2 = split_func(line)
            if tok1 not in token_map:
                token_map[tok1] = list()
            token_map[tok1].append(tok2)
    return token_map

def parse_smap_nodes(servicemap):
    pass

def parse_smap_links(servicemap):
    pass

def parse_smap_lbs(servicemap):
    pass

def parse_smap_clients(servicemap):
    pass

# servicemap can be a file or an HTTP endpoint
# TODO: use urlparse to check if is url
def route_parser(servicemap):
    if os.path.exists(servicemap):
        pass
