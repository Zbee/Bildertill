#Dependencies (Pillow, Unirest, Webcolors)
#pip install pillow unirest webcolors
import time, urllib2, urllib, simplejson, cStringIO, os, unirest, webcolors, ice
from PIL import Image

#Variables
boards = ["wg", "w"]
ratios = [16/9, 4/3, 16/10, 21/9, 21/10, 5/6]
extens = [".png", ".jpg"]

thisTime = time.strftime("%Y-%m-%dT%H%M%S")
os.makedirs(thisTime)
open(thisTime + "/"  + "log.txt", "a").close()
print "Commencing tagging at " + thisTime

#Scraping each defined board
x = 0
for board in boards:
  print "/" + board + "/"
  os.makedirs(thisTime + "/" + board)

  ##Load the thread number on the board
  threadsson = "https://a.4cdn.org/" + board + "/threads.json"
  req = urllib2.Request(
    threadsson,
    None,
    {'user-agent':'zbee/bildertill'}
  )
  opener = urllib2.build_opener()
  try:
    json = opener.open(req)
    data = simplejson.load(json)

    ##For each thread on the front page of the board
    for thread in data[0]["threads"]:
      print "     " + str(thread["no"])

      threadson = "https://a.4cdn.org/" + board + "/thread/" + str(thread["no"]) + ".json"
      req = urllib2.Request(
        threadson,
        None,
        {'user-agent':'zbee/bildertill'}
      )
      opener = urllib2.build_opener()
      try:
        json = opener.open(req)
        data = simplejson.load(json)

        ##Skip if the thread is a sticky
        if "sticky" in data["posts"][0]:
          print "             Sticky (skipping)"
          continue

        ##For each reply in the thread from the front page of the board
        for reply in data["posts"]:
          if "tim" in reply and reply["w"]/reply["h"] in ratios and reply["ext"] in extens and reply["w"]>800 and reply["h"]>600:
            img = str(reply["tim"]) + reply["ext"]
            url = "http://i.4cdn.org/" + board + "/" + img
            urllib.urlretrieve(url, thisTime + "/"  + board + "/" + img)
            os.rename(thisTime + "/"  + board + "/" + img, thisTime + "/"  + board + "/" + str(x) + reply["ext"])
            dlImg = thisTime + "/"  + board + "/" + str(x) + reply["ext"]
            x += 1

            print "             " + str(reply["no"]) + ": " + str(url)

            colors = []
            domColors = ice.colorz(dlImg)
            for color in domColors:
              rgbb = str(webcolors.hex_to_rgb(color))[1:-1].split(", ")
              rgb = []
              for r in rgbb:
                rgb.append(int(round((float(r)/255)*5)*51))

              actualName, closestName = ice.get_colour_name(tuple(rgb))
              colorName = actualName if actualName != None else closestName

              colors.append({color: colorName})

            response = unirest.get(
              "https://faceplusplus-faceplusplus.p.mashape.com/detection/detect?"
              + "attribute=glass%2Cpose%2Cgender%2Cage%2Crace%2Csmiling&url="
              + urllib.quote(img),
              headers = {
                "X-Mashape-Key": "",
                "Accept": "application/json"
              }
            )

            if "face" in response.body and len(response.body["face"]) > 0:
              person = response.body["face"]
            else:
              person = False

            tags = {
              "url": url,
              "colors": colors,
              "person": person
            }

            with open(thisTime + "/"  + "log.txt", "a") as myfile:
              myfile.write(str(tags) + "\n")

      except urllib2.HTTPError as e:
        pass
  except urllib2.HTTPError as e:
    pass