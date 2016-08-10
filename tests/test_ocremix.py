#!/usr/bin/env python3

import os
import responses
import requests
import unittest
from ocremix import OCRemixDownloader


class TestOCRemixDownloader(unittest.TestCase):
    def setUp(self):
        self.testee = OCRemixDownloader()
        self.source_url = "http://ocremix.org/remix/OCR03357"

    def test_get_download_link_from_page(self):
        actual = self.testee.get_download_link_from_page(self.source_url)
        assert "http://ocr.blueblue.fr/files/music/remixes/Final_Fantasy_9_The_Journey_Home_OC_ReMix.mp3" == actual

    def test_get_md5_sum_from_page(self):
        actual = self.testee.get_md5_sum_from_page(self.source_url)
        assert "fd95488024ec07b484eb597f9e133298" == actual

    def test_get_md5_from_file(self):
        actual = self.testee.get_md5_from_file("/home/yur763/media/music/OCREMIX/singles/Final_Fantasy_9_The_Journey_Home_OC_ReMix.mp3")
        assert "fd95488024ec07b484eb597f9e133298" == actual

    def test_download_and_write_file(self):
        mp3_url = self.testee.get_download_link_from_page(self.source_url)
        target_file = self.testee.download_and_write_file(mp3_url, "./")

        wanted = self.testee.get_md5_sum_from_page(self.source_url)
        actual = self.testee.get_md5_from_file(target_file.name)

        os.system("rm -f %s" % target_file.name)

        assert actual == wanted
