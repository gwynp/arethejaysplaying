# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from xml.etree import ElementTree
import requests
import time
import datetime
import urllib2
from twython import Twython
import os

API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.getenv('API_SECRET')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.getenv('OAUTH_TOKEN_SECRET')
SNS_TOPIC = os.environ.get("SNS_TOPIC")

print "the API KEY is %s" % API_KEY
print "the API SECRET is %s" % API_KEY_SECRET
print "the OAUTH_TOKEN is %s" % OAUTH_TOKEN
print "the OAUTH_TOKEN_SECRET is %s" % OAUTH_TOKEN_SECRET

teams = {
		"anamlb" : "Angels",
		"arimlb" : "Diamondbacks",
		"atlmlb" : "Braves",
		"balmlb" : "Orioles",
		"bosmlb" : "Red Sox",
		"chnmlb" : "Cubs",
		"chamlb" : "White Sox",
		"clemlb" : "Indians",
		"colmlb" : "Rockies",
		"detmlb" : "Tigers",
		"houmlb" : "Houston",
		"kcamlb" : "Royals",
		"lanmlb" : "Dodgers",
		"miamlb" : "Marlins",
		"milmlb" : "Brewers",
		"minmlb" : "Twins",
		"nyamlb" : "Yankees",
		"nymmlb" : "Mets",
		"oakmlb" : "A's",
		"phimlb" : "Phillies",
		"pitmlb" : "Pirates",
		"sdnmlb" : "Padres",
		"seamlb" : "Mariners",
		"sfnmlb" : "Giants",
		"slnmlb" : "Cardinals",
		"tbamlb" : "Rays",
		"texmlb" : "Rangers",
		"tormlb" : "Jays",
		"wasmlb" : "Nationals",
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
	# pull the opponent name from the URI.
	# it can be in one of two places in the string
	# so try both
	opponent = str(jaysuri[15:-9])
	if opponent == "tormlb":
		opponent = str(jaysuri[22:-2])
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
	return gametime, timezone, venue, homefirstname, homesurname, awayfirstname, awaysurname

# build the url and pull the page down into buetiful soup
year,month,month_word,day = get_date()
url = mlbbaseurl + "year_" + year + "/month_" + month + "/day_" + day
r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data,"html.parser")

# This pulls all the urls from the gameday index page and finds the one containing the Jays.
# there me be more than one game so build the string by appending game details
# The game values come from the gameday xml page
for link in soup.find_all('a'):
	if "gid" in str(link.get('href')) and "tormlb" in str(link.get('href')):
		message = 'Yes! '
		link_count = link_count + 1
		jaysuri = link.get('href')
		jaysuri = jaysuri[:-1]
		jaysdir = url + "/" + jaysuri
		opponent_name = get_opponent(jaysuri)
		(gametime, timezone, venue, homefirstname, homesurname, awayfirstname, awaysurname) = get_game_values(jaysdir)
		message += "against the %s at %s %s at %s \n%s %s against %s %s\n" % (opponent_name, gametime, timezone, venue, homefirstname, homesurname, awayfirstname, awaysurname)

	if link_count == 0:
		message = "Not Today"

twitter = Twython(API_KEY, API_KEY_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()
twitter.update_status(status=message)
sns = boto3.resource('sns')
topic = sns.Topic(SNS_TOPIC)
topic.publish(Message=message)
print message
