#!/usr/bin/env python3
import feedparser
import logging
import os
import re
import sys
import requests


class OCRemixDownloader():
    logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__)) + os.sep + 'ocremix.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s')

    def __init__(self, source_feed="http://www.ocremix.org/feeds/ten20/",
                 history_file=os.path.dirname(os.path.abspath(__file__)) +
                 os.sep + '.ocremix_history'):
        self.source_feed = source_feed
        self.history_file = history_file

    def parse_input_arguments(self):
        if len(sys.argv) < 3:
            print("""usage: ocremix.py title_filter_pattern
                    download_directory [debug]""",
                  file=sys.stderr)
            print("", file=sys.stderr)
            print("example: ocremix.py 'Sonic' 'downloads/'", file=sys.stderr)
            print("example: ocremix.py all '/media/music/OCREMIX/'",
                  file=sys.stderr)
            sys.exit(1)

        self.title_string = sys.argv[1]
        self.path_string = sys.argv[2]

        # debug mode?
        if len(sys.argv) == 4:
            debug_string = sys.argv[3]
        else:
            debug_string = None
        if debug_string:
            self.debug = True
        else:
            self.debug = False

    def parse_search_query(self):
        try:
            if re.match(r'all|everything', self.title_string) is not None:
                self.title_string = ''
                logging.debug("search query matches 'all'")
            self.title_regex = re.compile(".*" + self.title_string + ".*")
        except Exception:
            print("error: bad regular expression, " + self.title_string,
                  file=sys.stderr)

        # parse the download path
        self.path_prefix = os.path.expanduser(self.path_string)
        if not os.path.exists(self.path_prefix):
            print("error: directory " + self.path_prefix + " does not exist")
            sys.exit(1)
        logging.debug("using %s as target directory" % self.path_prefix)

    def parse_feed_and_get_page_links(self) -> [str]:
        feed = feedparser.parse(self.source_feed)
        logging.debug('parsed %s' % self.source_feed)
        links = []
        for item in feed["items"]:
            title = item['title']
            link = item['link']

            if link in self._history:
                logging.debug('%s is already in history file.' % title)
                if self.debug:
                    print(title)
                    print("   Skipping: Already in history file.\n\n")
                continue
            if self.title_regex.match(item['title']) is None:
                logging.debug('%s does not match input pattern' % title)
                if self.debug:
                    print(title)
                    print("   Skipping: Does not match input pattern %s\n\n" %
                          self.title_regex.pattern)
                continue

            links.append(link)
        return links

    def fetch_mp3s(self, page_urls: [str]) -> None:
            for page_url in page_urls:
                link_to_mp3 = self.get_download_link_from_page(page_url)
                self.download_and_write_file(link_to_mp3, self.path_prefix)
                self._history.append(page_url.strip())

    def get_download_link_from_page(self, url):
        response_body = requests.get(url).text
        # match the first *.mp3 url available
        match = re.findall('http:\/\/.*mp3', response_body)
        if match is not None:
            logging.debug("found download link: %s" % match[0])
            return match[0]
        else:
            return None

    def download_and_write_file(self, url, path_prefix):
        filename = url.split('/')[-1]
        path = os.path.normpath(path_prefix + os.sep + filename)
        if self.debug:
            print("   Downloading: %s" % url)
        http_response = requests.get(url)
        f = open(path, 'w+b')
        f.write(http_response.content)
        f.close()
        logging.debug('mp3 written to %s' % path)
        if self.debug:
            print("   Written: %s" % path)

    def read_history_from_disk(self):
        self._history = []
        if os.path.exists(self.history_file):
            logging.debug('%s found' % self.history_file)
            with open(self.history_file, "r") as f:
                contents = f.readlines()
                for line in contents:
                    self._history.append(line.strip())
        else:
            logging.debug('%s created' % self.history_file)
        logging.debug('%s read' % self.history_file)

    def write_history_to_disk(self):
        f = open(self.history_file, "w")
        logging.debug('%s found' % self.history_file)
        f.write('\n'.join(self._history))
        f.close()
        logging.debug('%s written' % self.history_file)

    def run(self):
        # set input arguments
        self.parse_input_arguments()

        # parse the search query
        self.parse_search_query()

        self.read_history_from_disk()
        links = self.parse_feed_and_get_page_links()
        self.fetch_mp3s(links)
        self.write_history_to_disk()

if __name__ == '__main__':
    OCRemixDownloader().run()
