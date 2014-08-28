# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from xml.etree import ElementTree
import requests
import time
import datetime
import urllib2
from twython import Twython
import os

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.getenv('APP_SECRET')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.getenv('OAUTH_TOKEN_SECRET')

print "the APP KEY is %s" % APP_KEY

teams = {
		"atlmlb" : "Braves",
		"bosmlb" : "Red Sox",
		"chnmlb" : "Cubs",
		"clemlb" : "Indians",
		"tormlb" : "Jays",
}
mlbbaseurl = "http://gd2.mlb.com/components/game/mlb/"
link_count=0
# reference - the MLB URL:
# http://gd2.mlb.com/components/game/mlb/year_2014/month_08/day_26/gid_2014_08_26_minmlb_kcamlb_1/inning/inning_all.xml 

def get_date():
	year = datetime.date.today().strftime("%Y")
	month = datetime.date.today().strftime("%m")
	month_word = datetime.date.today().strftime("%B")
	day = datetime.date.today().strftime("%d")
	return (year,month,month_word,day)

def get_opponent(jaysuri):
	opponent = str(jaysuri[15:-9])
	opponent_name = teams[opponent]
	return opponent_name

def get_game_values(jaysdir):
	gamecenter = jaysdir + '/gamecenter.xml'
	file = urllib2.urlopen(gamecenter)
	data = file.read()
	file.close()
	#print data
	tree = ElementTree.ElementTree(ElementTree.fromstring(data))
	#print tree
	root = tree.getroot()
	for name, value in root.attrib.items():
		if name == "start_time":
			gametime = value
		if name == "time_zone":
			timezone = value

	for node in tree.findall('./venueShort'):
		venue = node.text

	for node in tree.findall('./probables/home'):
		homesurname = node.find('lastName').text
		homefirstname = node.find('useName').text
		
	for node in tree.findall('./probables/away'):
		awaysurname = node.find('lastName').text
		awayfirstname = node.find('useName').text


	for name, value in root.attrib.items():
		if name == "start_time":
			gametime = value
		if name == "time_zone":
			timezone = value

# build the url and pull the page down into buetiful soup
year,month,month_word,day = get_date()
url = mlbbaseurl + "year_" + year + "/month_" + month + "/day_" + day
r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data)

# This pulls all the urls from the gameday index page and finds the one containing the Jays.
# there me be more than one game so build the string by appending game details
# The game values come from the gameday xml page
for link in soup.find_all('a'):
	if "gid" in str(link.get('href')) and "tormlb" in str(link.get('href')):
		message = 'Yes! '
		link_count += link_count
		jaysuri = link.get('href')
		jaysuri = jaysuri[:-1]
		jaysdir = url + "/" + jaysuri
		get_opponent(jaysuri)
		get_game_values(jaysdir)
		message += "against the %s at %s %s at %s \n%s %s against %s %s\n" % (opponent_name, gametime, timezone, venue, homefirstname, homesurname, awayfirstname, awaysurname)

	if link_count == 0:
		message = "Not Today"

twitter = Twython(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.update_status(status=message)
print message