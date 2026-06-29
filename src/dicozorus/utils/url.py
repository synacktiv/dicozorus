import re
from urllib.parse import urlparse

SYMBOLS = r'~!@#$\%^&_=\[\]|\:;,.\?\+\-\*/' # Removed : ()'"`{}<>
URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[' + \
                SYMBOLS + ']|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
HTTP_PATH_REGEX=r'(GET|POST|PUT|DELETE|OPTIONS|HEAD|CONNECT|TRACE|PATCH)' + \
                r'\s+(\S+)\s+HTTP'

def extract_urls(text, blacklist):
    """
    Find URLs in text using URL_REGEX
    if URL or PATH contains anything in the blacklist,
    the element will be rejected.
    return a list of strings
    """
    extracted_urls = []
    urls = re.findall(URL_REGEX, text)
    for url in urls:
        if not is_blacklisted(url, blacklist):
            extracted_urls.append(url)
    return extracted_urls

def extract_paths(text, blacklist):
    """
    Extract paths from URL and HTTP_requests present in text.
    URL must match URL_REGEX
    HTTP_requests must match HTTP_PATH_REGEX
    return a list of strings
    """
    paths_from_url = extract_paths_from_urls(text, blacklist)
    paths_from_http_reqs = extract_paths_from_http_reqs(text, blacklist)
    return paths_from_url + paths_from_http_reqs

def extract_paths_from_urls(text, blacklist):
    """
    Extract PATHs from text.
    First find all URLs in the text, then parse each URL to get the
    path element. if URL or PATH contains anything in the blacklist,
    the element will be rejected.
    return a list of strings
    """
    urls = extract_urls(text, blacklist)
    extracted_path = []
    for url in urls:
        try:
            path = urlparse(url).path
            if not is_blacklisted(path, blacklist):
                extracted_path.append(path.lstrip('/'))
        except ValueError:
            pass
    return extracted_path


def extract_paths_from_http_reqs(text, blacklist):
    """ Extact paths from HTTP requests using the regex HTTP_PATH_REGEX """
    http_paths = []
    http_matches = re.findall(HTTP_PATH_REGEX, text)
    for http_match in http_matches:
        path = urlparse(http_match[1]).path
        if not is_blacklisted(path, blacklist):
            http_paths.append(path.lstrip('/'))
    return http_paths

def is_blacklisted(entry, blacklist):
    """
    Checks if an entry is within a blacklist or not
    """
    return any(blacklisted_entry in entry for blacklisted_entry in blacklist)
