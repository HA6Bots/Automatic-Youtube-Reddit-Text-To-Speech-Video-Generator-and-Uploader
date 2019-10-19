import os
import generatorclient
import settings
from time import sleep
from threading import Thread
import pickle
import datetime
from datetime import timedelta
import videoscript
from pydub import AudioSegment
import random

#18:00 19:00 20:00 23:00 00:00 01:00

scriptIBuffer = []

def loadVideoScripts():
    vidsaves = os.listdir(settings.rawvideosaves)
    for vid in vidsaves:
        path = settings.rawvideosaves + "\\" + vid
        with open(path, 'rb') as pickle_file:
            script = pickle.load(pickle_file)
        videoscript.videoscripts.append(script)


def parseScripts():
    if scriptIBuffer:
        for script in scriptIBuffer:
            scriptno = script[0]
            print("Parsing Raw Script %s" % scriptno)
            scripttitle = script[1]
            author = script[2]
            ups = script[3]


            payload = script[4]
            final_script = payload[0]
            videotype = payload[1]
            video_settings = payload[2]
            music_type = payload[3]
            thumbnail = payload[4]
            characters_amount = payload[5]
            youtube_title = payload[6]
            youtube_description = payload[7]
            youtube_tags = payload[8]

            videoscript.VideoScriptEngine(scriptno, scripttitle, author, ups, final_script, videotype, video_settings, music_type, thumbnail, characters_amount, youtube_title, youtube_description, youtube_tags)
        scriptIBuffer.clear()
    else:
        print("VIDEO GENERATOR no scripts to parse")



def uploadVids():
    pass
    """
    if renderedVids:
        for vid in renderedVids:
            vid.generateMovie()
        renderedVids.clear()
        loadVideoScripts()
    """

def canUpload():
    if generatorclient.last_upload_times is not None:
        if generatorclient.last_upload_times == 0:
            return 6
        now = datetime.datetime.now()
        vids_within_day = 0
        for time in generatorclient.last_upload_times:
            time = time[0]
            difference = now - time
            if difference < timedelta(days=1):
                vids_within_day += 1
        print("%s Videos uploaded in the last 24 hours" % vids_within_day)
        print("Estimated quote usage %s" % (vids_within_day * 1658))
        if vids_within_day < 6:
            return (6 - vids_within_day)
        else:
            return generatorclient.last_upload_times[0]
    return False

def tickThread():
    while True:

        sleep(30)
        if generatorclient.last_upload_times is None and not generatorclient.isRequestingScripts:
            print("No update times available... requesting more")
            generatorclient.getLastUploadedScripts()
            sleep(5)

        if videoscript.videoscripts:
            print("Rendering all video scripts...")
            for script in videoscript.videoscripts:
                script.renderVideo()

            amount_to_upload = canUpload()

            if type(amount_to_upload) is int:
                scripts_available_to_upload = [script for i, script in enumerate(videoscript.videoscripts) if script.isRendered]
                print("Allowed to upload %s videos" % amount_to_upload)
                if amount_to_upload > len(scripts_available_to_upload):
                    amount_to_upload = len(scripts_available_to_upload)
                    print("Only %s scripts available to upload" % amount_to_upload)
                print("Uploading %s video scripts... %s ready to upload (total %s)" % (amount_to_upload, amount_to_upload, len(videoscript.videoscripts)))
                for i in range(0, amount_to_upload, 1):
                    scripts_available_to_upload[i].uploadVideo()
                generatorclient.last_upload_times = None
            elif type(amount_to_upload) is bool:
                print("Can't get last update times")
            else:
                print("Estimated out of quotes waiting till %s" % amount_to_upload)
        else:
            print("No video scripts, just chilling...")


        if not generatorclient.isRequestingScripts:
            generatorclient.requestScripts([script.scriptno for script in videoscript.videoscripts])





def initQueue():

    if not os.path.exists(settings.videoqueue_directory):
        os.mkdir(settings.videoqueue_directory)

    if not os.path.exists(settings.rawvideosaves):
        os.mkdir(settings.rawvideosaves)

    if not os.path.exists(settings.finishedvideosdirectory):
        os.mkdir(settings.finishedvideosdirectory)

    generatorclient.connectToServer()
    loadVideoScripts()
    sleep(2)
    generatorclient.requestScripts([script.scriptno for script in videoscript.videoscripts])
    thread = Thread(target=tickThread)
    thread.start()
    #uploadVids()

if __name__ == "__main__":
    initQueue()