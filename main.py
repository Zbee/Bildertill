#Dependencies (Pillow, Unirest, Webcolors)
#pip install pillow unirest webcolors
import sched, time, urllib2, urllib, simplejson, cStringIO, os, unirest, webcolors, ice
from PIL import Image

#Variables
boards = ["wg", "w"]
ratios = [16/9, 4/3, 16/10, 21/9, 21/10, 5/6]
extens = [".png", ".jpg"]

#Scheduling
s = sched.scheduler(time.time, time.sleep)
scrapes = 0
def scheduler(sc):
  global scrapes
  scrapes += 1
  thisTime = time.strftime("%Y-%m-%dT%H%M%S")
  os.makedirs(thisTime)
  print "Commencing scrape #" + str(scrapes) + " (" + thisTime + ")"
  scrape4chan(thisTime)
  sc.enter(15*60, 1, scheduler, (sc, ))

s.enter(0, 1, scheduler, (s, ))

#Scraping
def scrape4chan(thisTime):
  global ratios, boards, extens

  ##For each specified board
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

          ##For each reply in the thread from the front page of the board
          for reply in data["posts"]:
            if "tim" in reply and reply["w"]/reply["h"] in ratios and reply["ext"] in extens and reply["w"]>800 and reply["h"]>600:
              img = str(reply["tim"]) + reply["ext"]
              url = "http://i.4cdn.org/" + board + "/" + img
              urllib.urlretrieve(url, thisTime + "/"  + board + "/" + img)

              colors = []
              domColors = ice.colorz(thisTime + "/"  + board + "/" + img)
              for color in domColors:
                rgbb = str(webcolors.hex_to_rgb(color))[1:-1].split(", ")
                rgb = []
                for r in rgbb:
                  rgb.append(int(round((float(r)/255)*5)*51))

                actualName, closestName = ice.get_colour_name(tuple(rgb))
                colorName = actualName if actualName != None else closestName

                colors.append({color: colorName})

              response = unirest.get(
                "https://faceplusplus-faceplusplus.p.mashape.com/detection/detect?attribute=glass%2Cpose%2Cgender%2Cage%2Crace%2Csmiling&url=" + urllib.quote(img),
                headers={
                  "X-Mashape-Key": "",
                  "Accept": "application/json"
                }
              )
                
              if "face" in response.body and len(response.body["face"]) > 0:
                person = response.body["face"]
              else:
                person = False

              tags = {
                "colors": colors,
                "person": person
              }

              with open("log.txt", "a") as myfile:
                myfile.write(str(tags) + "\n")

        except urllib2.HTTPError as e:
          pass
    except urllib2.HTTPError as e:
      pass

#Run schedule
s.run()