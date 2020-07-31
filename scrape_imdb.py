#!/usr/bin/env python

import requests, re
from bs4 import BeautifulSoup
import re
import pymongo 
import sys 

"""Script scrape movies from imdb and put the strapped movies in a mongobd"""

__author__      = "Jah-Wilson Teeba"
__date__        = "July 30, 2020"
__copyright__   = "Copyright 2020"
__license__     = "MIT"
__version__     = "1.0"
__maintainer__  = "Jah-Wilson Teeba"
__email__       = "jteeba@widener.edu"
__status__      = "Production"



req  = requests.get("https://www.imdb.com/search/title/?year=2019-01-01,2019-01-31&start=0")
cont = req.content
soup = BeautifulSoup(cont,"html.parser")
all  = soup.find_all("div",{"class":"lister-item mode-advanced"})
page_nr = soup.find("div",{"class":"desc"}).text[9:15].replace(",", "")
page_nr = round(int(page_nr)/len(all))
print("Finished: Initial setup")

movies_list=[]
base_url = "https://www.imdb.com/search/title/?year=2019-01-01,2019-01-31&start=0"
print("Scrapping movies from IMDB, Will take few  minutes...")
for page in range(0,page_nr*50,50):
    r=requests.get(base_url+str(page))
    c=r.content
    soup=BeautifulSoup(c,"html.parser")
    all=soup.find_all("div",{"class":"lister-item mode-advanced"})
    for item in all:
        movies_dict = {}

        movies_dict["Title"] = item.find("h3", {"class":"lister-item-header"}).text.replace("\n", "")
        regex = re.sub('(^[\d+]+[\D])', '', movies_dict["Title"])
        regex = regex.split("(")[0]
        movies_dict["Title"] = regex
        movies_dict["Year"] = item.find("span", {"class":"lister-item-year text-muted unbold"}).text.replace("(", "").replace(")", "")
        try:
            movies_dict["Rating"] = item.find("span", {"class":"certificate"}).text
        except:
            movies_dict["Rating"] = None
        try:
            movies_dict["Genre"] = item.find("span", {"class":"genre"}).text.replace("\n", "").replace(" ", "")
        except:
            movies_dict["Genre"] = None

        try:
            movies_dict["Rating"] = item.find("div", {"class":"ratings-bar"}).text[3:6]
        except:
            movies_dict["Rating"] = None

        movies_dict["Descripton"] = item.find_all("p", {"class":"text-muted"})[1].text.replace("\n","")

        try:
            movies_dict["Time"] = item.find("span", {"class":"runtime"}).text
        except:
            movies_dict["Time"] = None

        movies_dict["Star"] = item.find_all("p", {"class":""})[0].text.replace("\n","").replace("Stars:","")
        movies_dict["Movie_Image"] = item.find("img", {"class":"loadlate"})["loadlate"]

        movies_list.append(movies_dict)
print("Finished: scrapping movies...")
print("Connecting to mongodb cloud...")
try:
    client = pymongo.MongoClient(port=27017)
except Exception as ex:
    print("Connection to mongodb cloud failed. Reason: {}".format(ex))
    sys.exit(1)
print("Successfully connected to mongodb cloud :)")

db=client["movies"]
collection = db["movies"]
for item in movies_list:
    collection.insert_one(item)
print("Finished adding data to database")
print("DONE :)")
