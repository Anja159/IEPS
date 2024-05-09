import json
import re
from bs4 import BeautifulSoup


def extractRegex(pages):
    extracted = []
    for page in pages:
        pageId = 1
        with open(page) as bs:
            soup = BeautifulSoup(bs, "html.parser")
            # print(soup)

            # if 'kitara1':
            #     print("k1")

            # if 'kitara2':
            #     print("k2")
            if 'kitara1' in str(soup):
                print("k1")

            if 'kitara2' in str(soup):
                print("k2")

            # with open(page, "rb") as file:
            #     # extracted[pageId] =
            # str(BeautifulSoup(file.read(), "html.parser"))
