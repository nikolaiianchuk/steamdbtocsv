import json
from urllib.request import urlretrieve
import time
import requests
import os
import sys


def console_log(s):
    print("[" + time.asctime() + "] " + s)


def iconsole_log(s):
    return str(input("[" + time.asctime() + "] " + s))


console_log("Downloading SteamID Database")
urlretrieve('https://steamspy.com/api.php?request=all', 'temp.json')
console_log("Parsing Downloaded SteamID Database")
f = open('temp.json', 'r')
pf = json.loads(f.read())
appids = []
for appid in pf:
    appids.append(appid)
f.close()
del pf
console_log("Removing temporary files")
os.remove('temp.json')
gamecount = str(len(appids))
console_log("Steam has " + gamecount + " id's")
flag = True
if os.path.isfile("output.csv"):
    if iconsole_log("File exists. Y - Rewrite, N - Check for errors: ").capitalize() != 'Y':
        flag = False  # Checking file from errors and continue writing in file
if (flag):
    f = open("output.csv", 'w', encoding="utf8")
else:
    try:
        f = open("output.csv", 'ab+')
        while f.read(1) != b"\n":  # Until EOL is found...
            f.seek(-2, os.SEEK_CUR)  # ...jump back the read byte plus one more
        data = f.readline().decode(sys.getfilesystemencoding())
        f.close()
        last_appid = data.split(',')[0]
        console_log("Last written appid: " + last_appid)
    except OSError:
        console_log("Empty or incorrect file. Creating a new one")
        f = open("output.csv", 'w', encoding="utf8")
        flag = True
counter = 1
for appid in appids:
    try:
        if (not flag) & (appid != last_appid):
            counter += 1  # This is gonna be a little bit hazy
            continue
        else:
            flag = True
            if appid == last_appid:
                counter += 1
                continue
    except NameError:
        last_appid = appid
    if (f.closed):  # Doing this to save file in case of fault
        f = open("output.csv", 'a', encoding="utf8")
    json_page = None
    while json_page is None:  # Check if there is any data
        console_log("Parsing game " + str(counter) + " of " + gamecount + " games")
        page = requests.get('http://store.steampowered.com/api/appdetails?appids=' + appid)
        json_page = json.loads(page.text)
        if json_page is None:
            console_log("Reached request limits... Waiting for 300 seconds.")
            time.sleep(300)
    try:
        data = json_page[appid]['data']
        s = ','.join([appid, data['name'].replace(",", ";"), ';'.join(data['developers']).replace(",", ";"), ';'.join(data['publishers']).replace(",", ";"), data['supported_languages'].replace(",", ";"), str(data['website']), str(data['release_date']['date']).replace(",", ";"), str(data['release_date']['coming_soon']), str(data['support_info']['email']).strip(u'\u200b'), data['support_info']['url']])
        f.write((s + '\n'))
        console_log("ID: " + appid + " \"" + data['name'] + "\" has been written in output.csv")
    except KeyError:
        console_log("KeyError on AppID: " + appid + ". This is not a game.")
    counter += 1
    f.close()
