#Dependencies (Pillow)
import sched, time, urllib2, urllib, simplejson, cStringIO, os, Tkinter as tk
from PIL import Image, ImageTk

#Variables
boards = ["wg", "w"]
ratios = [16/9, 4/3, 16/10, 21/9, 21/10, 5/6]
extens = [".png", ".jpg"]
tor = 1

#Scheduling
s = sched.scheduler(time.time, time.sleep)
scrapes = 0
def scheduler(sc):
  global scrapes, tor
  tor = 15*60
  scrapes += 1
  os.makedirs(str(scrapes))
  print "Commencing scrape #" + str(scrapes)
  scrape4chan()
  sc.enter(tor, 1, scheduler, (sc, ))

s.enter(tor, 1, scheduler, (s, ))

#Scraping
def scrape4chan():
  global ratios, boards, extens, scrapes
  for board in boards:
    print "/" + board + "/"
    os.makedirs(str(scrapes) + "/" + board)

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

          for reply in data["posts"]:
            if "tim" in reply and reply["w"]/reply["h"] in ratios and reply["ext"] in extens:
              img = "http://i.4cdn.org/" + board + "/" + str(reply["tim"]) + reply["ext"]
              file = cStringIO.StringIO(urllib.urlopen(img).read())
              urllib.urlretrieve(img, str(scrapes) + "/"  + board + "/" +str(reply["tim"]) + reply["ext"])

        except urllib2.HTTPError as e:
          pass
    except urllib2.HTTPError as e:
      pass

#Run schedule
s.run()