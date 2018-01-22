from ElasticSearch import elastic_utils as es
import re
import os
import sys
import requests
import json
import nltk
import nltk
from bs4 import BeautifulSoup
from html2text import html2text
import mechanicalsoup
#DIFF_BOT_TOKEN = '6314736e3fead58866bf29cb1b67fba4'


#def create_bulk_job(urls, name):
#    apiUrl = 'http://api.diffbot.com/v3/article'
#    params = dict(token=DIFF_BOT_TOKEN, name=name, urls=urls, apiUrl=apiUrl)
#    response = requests.post('http://api.diffbot.com/v3/bulk', data=params)
#    return json.loads(response.content)

#https://stackoverflow.com/questions/26002076/python-nltk-clean-html-not-implemented
def clean_html(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.

    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()



print ("good!")
res = es.iterate_search("databreach")
url_list = []


for entry in res:
    entry = entry["_source"]["text"]
    results = re.search("(?P<url>https?://[^\s]+)", entry.strip())
    if results:

        url_list.append(results.group("url"))
        br = mechanicalsoup.StatefulBrowser()
      #  br.addheaders = [('User-agent', 'Firefox')]
        br.open(results.group("url"))
        html = br.get_current_page()
        cleanhtml = clean_html(str(html))
        text = html2text(cleanhtml)
       # soup = BeautifulSoup(html)
      #  text2 = soup.get_text()
        print("------------")
        print (text)
      #  print ("---------")
#        print (text2)




