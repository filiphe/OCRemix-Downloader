#!/usr/bin/env python3
import feedparser
import os
import re
import sys
import urllib3

http = urllib3.PoolManager()

SOURCE_FEED = "http://www.ocremix.org/feeds/ten20/"
HISTORY_FILE = os.path.dirname(__file__) + os.sep + '.ocremix_history'

# set input arguments
if len(sys.argv) < 3:
    print("usage: ocremix.py title_filter_pattern download_directory [debug]", file=sys.stderr)
    print("", file=sys.stderr)
    print("example: ocremix.py 'Sonic' 'downloads/'", file=sys.stderr)
    print("example: ocremix.py all '/media/music/OCREMIX/'", file=sys.stderr)
    sys.exit(1)

title_string = sys.argv[1]
path_string = sys.argv[2]

# debug mode?
if len(sys.argv) == 4:
    debug_string = sys.argv[3]
else:
    debug_string = None
if debug_string:
    debug = True
else:
    debug = False

# parse the search query
try:
    if re.match(r'all|everything', title_string) is not None:
        title_string = ''
    title_regex = re.compile(".*" + title_string + ".*")
except Exception:
    print("error: bad regular expression, " + title_string, file=sys.stderr)

# parse the download path
path_prefix = os.path.expanduser(path_string)
if not os.path.exists(path_prefix):
    print("error: directory " + path_prefix + " does not exist")
    sys.exit(1)


def get_download_link_from_page(url):
    response_body = http.request('GET', url).data.decode("utf-8")
    # match the first *.mp3 url available
    match = re.findall('http:\/\/.*mp3', response_body)
    if match is not None:
        return match[0]
    else:
        return None

def download_and_write_file(url, path_prefix):
    filename = url.split('/')[-1]
    path = os.path.normpath(path_prefix + os.sep + filename)
    if debug:
        print("   Downloading: %s" % url)
    http_response = http.request('GET', url)
    f = open(path, 'w+b')
    f.write(http_response.data)
    f.close()
    if debug:
        print("   Written: %s" % path)

def read_history_from_disk():
    d = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            contents = f.readlines()
            for line in contents:
                d.append(line.strip())
    return d

def write_history_to_disk(d):
    f = open(HISTORY_FILE, "w")
    f.write('\n'.join(d))
    f.close()

feed = feedparser.parse(SOURCE_FEED)
d = read_history_from_disk()
for item in feed["items"]:
    title = item['title']

    if title in d:
        if debug:
            print(title)
            print("   Skipping: Already in history file.\n\n")
        continue
    if title_regex.match(item['title']) is None:
        if debug:
            print(title)
            print("   Skipping: Does not match input pattern %s\n\n" % title_regex.pattern)
        continue

    page_url = item['link'].replace("www.", "")
    link_to_mp3 = get_download_link_from_page(page_url)
    download_and_write_file(link_to_mp3, path_prefix)
    d.append(title.strip())

write_history_to_disk(d)

