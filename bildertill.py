# Python 2.7

# Dependencies (Pillow, Unirest, Webcolors)
# pip install pillow unirest webcolors
import ice
import os
import simplejson
import time
import unirest
import urllib
import urllib2
import webcolors

# Configuration
boards = ["wg", "w"]
ratios = [16 / 9, 4 / 3, 16 / 10, 21 / 9, 21 / 10, 5 / 6]
extens = [".png", ".jpg"]

# Touch directory for this tagging
thisTime = time.strftime("%Y-%m-%dT%H%M%S")
os.makedirs(thisTime)

# Touch log file
open(thisTime + "/" + "log.txt", "a").close()

print "Commencing tagging at " + thisTime


# Processing a single image
def process_reply(reply, board):
    global x
    # If it's an image and meets the ratio requirements
    if "tim" in reply and reply["w"] / reply["h"] in ratios and \
            reply["ext"] in extens and reply["w"] > 800 and reply["h"] > 600:
        # Form image url
        img = str(reply["tim"]) + reply["ext"]
        url = "http://i.4cdn.org/" + board + "/" + img
        # Download image
        urllib.urlretrieve(
            url,
            thisTime + "/" + board + "/" + img
        )
        # Rename to a sequential number for this board
        os.rename(
            thisTime + "/" + board + "/" + img,
            thisTime + "/" + board + "/" + str(x) + reply["ext"]
        )
        # Form the path to the image
        dl_img = thisTime + "/" + board + "/" + str(x) + reply["ext"]
        x += 1

        try:
            # Determine dominant colors, in hexadecimal
            colors = []
            try:
                dominant_colors = ice.colorz(dl_img)
            except ZeroDivisionError:
                dominant_colors = []
            # For each dominant color, find closest web-safe color
            for color in dominant_colors:
                rgbb = str(webcolors.hex_to_rgb(color))[1:-1].split(
                    ", ")
                rgb = []
                for r in rgbb:
                    rgb.append(
                        int(round((float(r) / 255) * 5) * 51))

                actual_name, closest_name = ice.get_colour_name(
                    tuple(rgb)
                )
                # Use the closest name if no exact name was available
                if actual_name is not None:
                    color_name = actual_name
                else:
                    color_name = closest_name

                colors.append({color: color_name})
        except TypeError:
            colors = []

        # Check if there is a face present
        response = unirest.get(
            "https://faceplusplus-faceplusplus.p.mashape.com/detection/detect?"
            + "attribute=glass%2Cpose%2Cgender%2Cage%2Crace%2Csmiling&url="
            + urllib.quote(img),
            headers={
                "X-Mashape-Key": "",
                "Accept": "application/json"
            }
        )

        # If a person was found
        if "face" in response.body and len(
            response.body["face"]) > 0:
            person = response.body["face"]
        else:
            person = False

        # Form all collected tags
        tags = {
            "url": url,
            "colors": colors,
            "person": person
        }

        # Log tags
        with open(thisTime + "/" + "log.txt", "a") as myfile:
            myfile.write(str(tags) + "\n")

        del tags["url"]
        print "    " + str(reply["no"]) + ": " + str(url) + " " + \
              str(tags)


# Scraping each defined board
x = 0
for board in boards:
    print "/" + board + "/"

    # Create directory for board
    os.makedirs(thisTime + "/" + board)

    # Load the threads on the board
    threadsson = "https://a.4cdn.org/" + board + "/threads.json"
    req = urllib2.Request(
        threadsson,
        None,
        {'user-agent': 'zbee/bildertill'}
    )
    opener = urllib2.build_opener()
    try:
        json = opener.open(req)
        data = simplejson.load(json)

        # For each thread on the front page of the board
        for thread in data[0]["threads"]:
            print "  " + str(thread["no"])

            # Download thread's JSON
            threadson = "https://a.4cdn.org/" + board + "/thread/" + str(
                thread["no"]) + ".json"
            req = urllib2.Request(
                threadson,
                None,
                {'user-agent': 'zbee/bildertill'}
            )
            opener = urllib2.build_opener()
            try:
                json = opener.open(req)
                data = simplejson.load(json)

                # Skip if the thread is a sticky
                if "sticky" in data["posts"][0]:
                    print "    Sticky (skipping)"
                    continue

                # For each reply in the thread from the front page of the board
                for reply in data["posts"]:
                    process_reply(reply, board)

            except urllib2.HTTPError as e:
                pass
    except urllib2.HTTPError as e:
        pass

thisTime = time.strftime("%Y-%m-%dT%H%M%S")
print "Terminating tagging at " + thisTime
