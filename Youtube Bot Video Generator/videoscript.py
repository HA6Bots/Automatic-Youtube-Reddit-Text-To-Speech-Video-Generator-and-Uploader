import settings
import cv2
from VideoTypes import imageframe, standardredditformat
import generatemovie
import generatorclient
import datetime
import os
import shutil
import videouploader
import random
import pickle
from time import sleep


videoscripts = []

class VideoScriptEngine():

    def __init__(self, scriptno=None, scripttitle=None, author=None, ups=None,  final_script=None, videotype=None,
                 video_settings=None, music_type=None, thumbnail=None, characters_amount=None, youtube_title=None,
                 youtube_description=None, youtube_tags=None):
        self.scriptno = scriptno
        self.final_script = final_script
        self.scripttitle = scripttitle
        self.author = author
        self.ups = ups
        self.videotype = videotype
        self.video_settings = video_settings
        self.music_type = music_type
        self.thumbnail = thumbnail
        self.characters_amount = characters_amount
        self.youtube_title = youtube_title
        self.youtube_description = youtube_description
        self.youtube_tags = youtube_tags

        standard_path = settings.finishedvideosdirectory + "/vid%s/" % self.scriptno
        self.vid_path = standard_path + "vid%s.mp4" % self.scriptno
        self.vid_description = standard_path + "description.txt"
        self.vid_thumbnail = standard_path + "thumbnail.png"
        self.vid_tags = standard_path + "youtubetags.txt"
        self.vid_title = standard_path + "youtubetitle.txt"

        self.isRendered = False
        videoscripts.append(self)
        self.save()

    def renderVideo(self):
        if not self.isRendered:
            print("Started Rendering Script %s" % self.scriptno)
            imageframe.deleteAllFilesInPath(settings.tempPath)
            try:
                video_format = standardredditformat.StandardReddit("test", self.video_settings, self.music_type)
                formatted_script = imageframe.parseScript(self.final_script)
                newMovie = generatemovie.Movie(video_format, formatted_script,
                                               (self.author, self.scripttitle, self.ups), self.scriptno)
                export_location = newMovie.renderVideo()
                try:
                    cv2.imwrite(export_location + "/thumbnail.png", cv2.cvtColor(self.thumbnail, cv2.COLOR_RGB2BGR))
                except Exception:
                    pass
                writeTextToFile(export_location + "/description.txt", self.youtube_description)
                writeTextToFile(export_location + "/youtubetitle.txt", self.youtube_title)
                writeTextToFile(export_location + "/youtubetags.txt", self.youtube_tags)
            except Exception as e:
                print(e)
                print("Sorry, a error occured rendering this video. Skipping it")
            self.isRendered = True
            self.save()
            if settings.exportOffline:
                generatorclient.updateUploadDetails(self.scriptno, None, None)
                deleteRawSave(self.scriptno)
                videoscripts.remove(self)
                print("Video Successfully exported offline")


        else:
            print("VID GEN script %s already rendered" % self.scriptno)

    def save(self):
        path_name = settings.rawvideosaves + "\\rawvideo%s.save" % self.scriptno
        with open(path_name, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)
        print("VID GEN Saved vid %s to %s" % (self.scriptno, path_name))

    def uploadVideo(self):
        description = (loadTextFile(self.vid_description)).encode("utf8")
        title = (loadTextFile(self.vid_title)).encode("utf8")
        tags = loadTextFile(self.vid_tags)
        # title, description, tags, thumbnailpath, filepath
        time_to_upload = calculateUploadTime()
        print("Uploading video %s, sceduled release %s" % (self.scriptno, time_to_upload))
        success = videouploader.upload(title, description, tags, self.vid_thumbnail, self.vid_path,
                                       time_to_upload.replace(" ", "T") + ".0Z")
        if success:
            print("Successfully Uploaded video %s" % self.scriptno)
            now = datetime.datetime.now()
            time_uploaded = now.strftime('%Y-%m-%d %H:%M:%S')
            generatorclient.updateUploadDetails(self.scriptno, time_uploaded, time_to_upload)
            print("Done Uploading Video %s" % self.scriptno)
            videoscripts.remove(self)
            deleteRenderedVideoFolder(self.scriptno)
        else:
            return False


def loadTextFile(file):
    f = open(file, "r", encoding="utf8")
    content = f.read()
    f.close()
    return content

def writeTextToFile(location, text):
    with open(location, "w", encoding="utf8") as text_file:
        text_file.write(text)


def deleteRawSave(scriptno):
    try:
        path = settings.rawvideosaves + "/rawvideo%s.save" % scriptno
        os.remove(path)
        print("Removed raw save %s at %s" % (scriptno, path))
    except FileNotFoundError:
        print("Couldn't find save and delete for %s" % scriptno)

def deleteRenderedVideoFolder(scriptno):
    shutil.rmtree(settings.finishedvideosdirectory + "/vid%s" % scriptno)
    deleteRawSave(scriptno)

def calculateUploadTime():
    now = datetime.datetime.now()
    random_hour = random.randint(16, 18)
    suggested = now.replace(hour=random_hour)
    if suggested < now:
        suggested=now.replace(hour=now.hour + 2)
    suggested = suggested.replace(minute=0, second=0, microsecond=0)
    return suggested.strftime('%Y-%m-%d %H:%M:%S')
