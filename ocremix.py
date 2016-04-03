#!/usr/bin/env python3
import feedparser
import os
import re
import sys
import urllib3

http = urllib3.PoolManager()

SOURCE_FEED = "http://www.ocremix.org/feeds/ten20/"
HISTORY_FILE = os.path.dirname(__file__) + os.sep + '.ocremix_history'

if len(sys.argv) < 3:
    print("usage: ocremix.py title_filter_pattern download_directory [debug]", file=sys.stderr)
    print("", file=sys.stderr)
    print("example: ocremix.py 'Sonic' 'downloads/'", file=sys.stderr)
    print("example: ocremix.py all '/media/music/OCREMIX/'", file=sys.stderr)
    sys.exit(1)

title_string = sys.argv[1]
path_string = sys.argv[2]
if len(sys.argv) == 4:
    debug_string = sys.argv[3]
else:
    debug_string = None

try:
    if re.match('/all|everything/', title_string) is not None:
        title_string = ''
except Exception:
    print("error: bad regular expression, " + title_string, file=sys.stderr)

if re.match('/iTunes/', path_string) is not None:
    path_string = "~/Music/iTunes/iTunes Media/Automatically Add to iTunes/"
path_prefix = os.path.expanduser(path_string)
if not os.path.exists(path_prefix):
    print("error: directory " + path_prefix + " does not exist")
    sys.exit(1)

if debug_string:
    debug = True
else:
    debug = False

def get_download_link_from_page(url):
    response_body = http.request('GET', url).data.decode("utf-8")
    match = re.findall('http:\/\/.*mp3', response_body)
    if match is not None:
        return match[0]
    else:
        return None

def download_and_write_file(url, path_prefix):
    filename = url.split('/')[-1]
    path = path_prefix + filename
    if debug:
        print("   Downloading: %s" % url)
    http_response = http.request('GET', url)
    f = open(path, 'w+b')
    f.write(http_response.data)
    f.close()
    if debug:
        print("   Written: %s" % path)

feed = feedparser.parse(SOURCE_FEED)
for item in feed["items"]:
    download_url = item['link'].replace("www.", "")
    link_to_mp3 = get_download_link_from_page(download_url)
    download_and_write_file(link_to_mp3, path_prefix)


