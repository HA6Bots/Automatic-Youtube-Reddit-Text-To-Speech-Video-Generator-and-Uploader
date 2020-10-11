import os
import settings
settings.generateConfigFile()
import soundfile as sf
from pydub import AudioSegment
import generatorclient
from time import sleep
from subprocess import *
import videouploader
from threading import Thread
import pickle
import datetime
from datetime import timedelta
from PIL import Image
import subprocess
import videoscript
import random
from moviepy.editor import *

# 18:00 19:00 20:00 23:00 00:00 01:00

waitTill = None
scriptIBuffer = []


def loadVideoScripts():
    vidsaves = os.listdir(settings.rawvideosaves)
    print(vidsaves)
    for vid in vidsaves:
        if "DS_Store" in vid:
            continue
        path = settings.rawvideosaves + "/" + vid
        with open(path, 'rb') as pickle_file:
            script = pickle.load(pickle_file)
        videoscript.videoscripts.append(script)


def parseScripts():
    for musicType in generatorclient.musicTypes:
        if not os.path.exists(settings.assetPath + "/Music/%s" % musicType):
            print("Creating Music Path for %s: %s" % (musicType, settings.assetPath + "/Music/%s" % musicType))
            os.makedirs(settings.assetPath + "/Music/%s" % musicType)
        if len(os.listdir(settings.assetPath + "/Music/%s/" % musicType)) == 0:
            print("Music folder %s is empty! Please add mp3 files into this folder and restart the bot!" % (settings.assetPath + "/Music/%s/" % musicType))
            while True:
                sleep(10)
                print("Music folder %s is empty! Please add mp3 files into this folder and restart the bot!" % (
                            settings.assetPath + "/Music/%s/" % musicType))
                pass

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

            videoscript.VideoScriptEngine(scriptno, scripttitle, author, ups, final_script, videotype, video_settings,
                                          music_type, thumbnail, characters_amount, youtube_title, youtube_description,
                                          youtube_tags)
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
            return settings.uploads_a_day
        now = datetime.datetime.now()
        vids_within_day = 0
        for time in generatorclient.last_upload_times:
            time = time[0]
            if now.hour >= settings.youtube_api_quota_reset_hour:
                if time > now.replace(hour=settings.youtube_api_quota_reset_hour, minute=0, second=0):
                    vids_within_day += 1
            else:
                if time >= now - timedelta(days=1):
                    vids_within_day += 1
        print("%s Videos uploaded since %s:00" % (vids_within_day, settings.youtube_api_quota_reset_hour))
        print("Estimated quote usage %s" % (vids_within_day * 1658))
        return settings.uploads_a_day - vids_within_day
    return False


def tickThread():
    global waitTill
    while True:
        sleep(5)
        if generatorclient.last_upload_times is None and not generatorclient.isRequestingScripts:
            print("No update times available... requesting more")
            generatorclient.getLastUploadedScripts()
            sleep(5)

        if videoscript.videoscripts:
            print("Rendering all video scripts...")
            for script in videoscript.videoscripts:
                script.renderVideo()

            if waitTill is not None:
                if datetime.datetime.now() > waitTill:
                    waitTill = None
                else:
                    print("Out of Quote Response... waiting till %s" % waitTill)

            if settings.exportOffline:
                waitTill = None


            if not settings.exportOffline:
                if waitTill is None:
                    amount_to_upload = canUpload()

                    if type(amount_to_upload) is int:
                        scripts_available_to_upload = [script for i, script in enumerate(videoscript.videoscripts) if
                                                       script.isRendered]
                        print("Allowed to upload %s videos" % amount_to_upload)
                        if amount_to_upload > len(scripts_available_to_upload):
                            amount_to_upload = len(scripts_available_to_upload)
                            print("Only %s scripts available to upload" % amount_to_upload)
                        print("Uploading %s video scripts... %s ready to upload (total %s)" % (
                        amount_to_upload, amount_to_upload, len(videoscript.videoscripts)))
                        for i in range(0, amount_to_upload, 1):
                            upload = scripts_available_to_upload[i].uploadVideo()
                            try:
                                if upload is False:
                                    now = datetime.datetime.now()
                                    if now.hour > settings.youtube_api_quota_reset_hour:
                                        waitTill = now.replace(hour=settings.youtube_api_quota_reset_hour, minute=0, second=0) + timedelta(days=1)
                                    else:
                                        waitTill = now.replace(hour=settings.youtube_api_quota_reset_hour, minute=0, second=0)
                            except Exception as e:
                                print(e)
                                pass

                generatorclient.last_upload_times = None
            # elif type(amount_to_upload) is bool:
            #     print("Can't get last update times")
            else:
                print("Estimated out of quotes waiting till %s" % waitTill)
        else:
            print("No video scripts, just chilling...")

        if not generatorclient.isRequestingScripts:
            generatorclient.requestScripts([script.scriptno for script in videoscript.videoscripts])


def initQueue():
    ##    process = subprocess.call("wine /home/royalreddit/Desktop/balcon/balcon.exe -t supnerds -w /home/royalreddit/Desktop/test2.wav", shell = True)

    if not os.path.exists(settings.videoqueue_directory):
        os.mkdir(settings.videoqueue_directory)

    if not os.path.exists(settings.rawvideosaves):
        os.mkdir(settings.rawvideosaves)

    if not os.path.exists(settings.finishedvideosdirectory):
        os.mkdir(settings.finishedvideosdirectory)

    if not os.path.exists(settings.overlayPath):
        os.mkdir(settings.overlayPath)

    if not os.path.exists(f"{settings.currentPath}/TempVids"):
        os.mkdir(f"{settings.currentPath}/TempVids")



    loadVideoScripts()
    generatorclient.connectToServer()
    sleep(2)
    generatorclient.requestScripts([script.scriptno for script in videoscript.videoscripts])
    thread = Thread(target=tickThread)
    thread.start()
    # uploadVids()


if __name__ == "__main__":

    begin = True

    if not settings.exportOffline:
        videouploader.get_credentials()
    else:
        print("Video Generator launching in export offline mode")

    if not settings.noSpeech:
        if settings.use_balcon and settings.use_google_tts:
            print("You have selected to use both google tts and balcon tts! Please only select one in the config file!")
            begin = False

        if not settings.use_balcon and not settings.use_google_tts:
            print("You have not selected any tts options in the config file!"
                  " Please set either google tts or balcon tts to true! Not both!")
            begin = False

        if settings.use_balcon:
            command = "%s -t \"%s\" -n %s" % (settings.balcon_location,
                                                    "Balcon Voice Success", settings.balcon_voice)

            process = subprocess.call(command, shell=True)
            if process != 0:
                print("Balcon not found. This will work when the following command works in your commandline: %s" % ("%s -t \"%s\" -n %s" % (settings.balcon_location,
                                                    "Balcon Voice Test", settings.balcon_voice)))
                begin = False

    if settings.use_overlay:
        if not os.path.exists(f"{settings.overlayPath}/{settings.overlay_image}"):
            print(f"Overlay image {settings.overlayPath}/{settings.overlay_image} does not exist! Fix the file name in config.ini or set use_overlay=False")

            begin = False
        else:
            im = Image.open(f"{settings.overlayPath}/{settings.overlay_image}")
            width, height = im.size
            if width != 1920 or height != 1080:
                print(f"Overlay image {settings.overlayPath}/{settings.overlay_image} not of correct dimensions ({width},{height})! Needs to be 1920x1080")
                begin = False

    if begin:
        initQueue()
