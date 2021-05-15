
import datetime
import settings
import os
import pickle
import client

video_scripts = []
currentPath = os.path.dirname(os.path.realpath(__file__))


class VideoScript():
    def __init__(self, vidno, scriptno, submission_id, category, title, author, upvotes, comments, videotype, commentInformation, music_type, status, commentsamount, editedby = None):
        self.sub_reddit = category

        self.title = title
        self.youtube_title = None
        self.youtube_description = None
        self.youtube_tags = None
        self.submission_id = submission_id
        self.videoType = videotype
        self.upvotes = upvotes
        self.author = author
        self.commentInformation = commentInformation
        self.loadDefaultVideoSettings()
        self.music_type = music_type
        self.final_script = None
        self.parsedCommentInformation = []
        self.comments = comments
        self.beingEdited = False
        self.vidNo = vidno
        self.scriptno = scriptno
        vidsaves = os.listdir(settings.scriptsaves)
        self.scriptWrapper = ScriptWrapper(self.commentInformation, self.title, self.scriptno)

        self.thumbnail = None
        self.charactersAmount = None
        self.amount_comments = commentsamount
        self.status = status
        self.editedby = editedby
        video_scripts.append(self)

    def loadDefaultVideoSettings(self):
        self.videosettings = loadDefaultVideoSettings(self.videoType)

    def exportOffline(self):
        export_path = currentPath + "/Export/video%s.vid" % self.vidNo
        with open(export_path, 'wb') as pickle_file:
            pickle.dump((self.title, self.videoType, self.upvotes, self.author, self.videosettings, self.music_type, self.final_script), pickle_file)
        client.flagscript(self.scriptno, "MANUALCOMPLETE")

    def sendToServer(self):
        self.charactersAmount = self.scriptWrapper.getEditedCharacterCount()
        client.formatVideoScript(self)



def loadDefaultVideoSettings(videoformattype):
    if videoformattype == "standardredditformat":
        return    {"imageSize": [1920, 1080],
                  "hasBoundingBox" : False,
                   "hasUpvoteButton": True,
                   "bounding_box_colour" : [0, 255, 0, 256],
                  "background_color": [25, 25, 25],
                  "comment_text_color": [215, 218, 220],
                  "author_text_color": [89, 89, 89],
                  "author_details_color": [74, 175, 238],
                  "characters_per_line": 125,
                  "punctuationList": [",", "."],
                   "upvote_gap_scale_x": 1,
                   "upvote_gap_scale_y": 0.2,
                   "upvote_fontsize_scale": 2,
                  "reply_characters_factorX": 3,
                  "reply_fontsize_factorX": 0.625,
                  "reply_fontsize_factorY": 1.15384,
                  "comment_author_factor": 0.9,
                  "preferred_font_size": 30}



class CommentWrapper():
    def __init__(self, author, text, upvotes, subcomments = None):
        self.author = author
        self.text = text
        self.upvotes = upvotes
        self.subcomments = subcomments


class ScriptWrapper():
    def __init__(self, script, title, scriptno):
        self.title = title
        self.rawScript = script
        self.scriptno = scriptno
        self.scriptMap = []
        self.setupScriptMap()

    def setupScriptMap(self):
        for mainComment in self.rawScript:
            line = ()
            for subComment in mainComment:
                line = line + (False,)
            self.scriptMap.append(line)


    def keep(self, mainCommentIndex, childIndex):
        commentThread = self.scriptMap[mainCommentIndex]
        newThread = ()
        for i, comment in enumerate(commentThread):
            if not i == childIndex:
                newThread = newThread + (comment,)
            else:
                newThread = newThread + (True,)

        self.scriptMap[mainCommentIndex] = newThread

    def skip(self, mainCommentIndex, childIndex):
        commentThread = self.scriptMap[mainCommentIndex]
        newThread = ()
        for i, comment in enumerate(commentThread):
            if not i == childIndex:
                newThread = newThread + (comment,)
            else:
                newThread = newThread + (False,)

        self.scriptMap[mainCommentIndex] = newThread

    def moveDown(self, i):
        if i > 0:
            copy1 = self.scriptMap[i-1]
            copy2 = self.rawScript[i-1]

            self.scriptMap[i-1] = self.scriptMap[i]
            self.rawScript[i-1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at bottom!")

    def moveUp(self, i):
        if i < len(self.scriptMap) - 1:
            copy1 = self.scriptMap[i+1]
            copy2 = self.rawScript[i+1]

            self.scriptMap[i+1] = self.scriptMap[i]
            self.rawScript[i+1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at top!")

    def setCommentData(self, x, y, text):
        self.rawScript[x][y].text = text

    def getCommentData(self, x, y):
        return self.rawScript[x][y]

    def getCommentAmount(self, mainCommentIndex):
        return len(self.scriptMap[mainCommentIndex])

    def getCommentThreadsAmount(self):
        return len(self.scriptMap)

    def getEditedCommentThreadsAmount(self):
        return len([commentThread for commentThread in self.scriptMap if commentThread[0] is True])

    def getEditedCommentAmount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        count = 0
        for commentThread in commentThreads:
            for comment in commentThread:
                if comment is True:
                    count += 1
        return count

    def getEditedWordCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text.split(" "))
        return word_count

    def getEditedCharacterCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text)
        return word_count

    def getEstimatedVideoTime(self):
        """
        estimation:
        -animation time between different commentthreads
        -total words
        """
        time = datetime.timedelta()
        word_count = self.getEditedWordCount()
        word_count += len(self.title.replace(" ", ""))
        if not word_count == 0:
            mins = word_count / settings.wordsPerMinute
            time += datetime.timedelta(minutes=mins)
        return time

    def getCommentInformation(self, x, y):
        comments = []
        commentThread = []
        for i, commentWrapper in enumerate(self.rawScript[x]):
            if i < y + 1:
                commentThread.append(commentWrapper)
        comments.append(tuple(commentThread))
        return comments

    def isRecommendedLength(self):
        if self.getEstimatedVideoTime() < settings.recommendedLength:
            return False
        return True

    def saveScriptWrapper(self):
        path_name = settings.scriptsaves + "/rawvideo%s.save" % self.scriptno
        with open(path_name, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    def convertToFormat(self):
        final_script = []
        for x, commentThread in enumerate(self.rawScript):
            thread = ()
            for y, comment in enumerate(commentThread):
                if self.scriptMap[x][y]:
                    thread = thread + ((comment.author, comment.text, comment.upvotes),)
            if not thread == ():
                final_script.append(thread)
        return final_script


def getCategories():
    return [value.sub_reddit for value in video_scripts]

def getScripts():
    return [value.vidNo for value in video_scripts]

def updateScriptStatus(scriptno, status, editedby):
    if scriptno is not None:
        try:
            scriptnos = [script.scriptno for script in video_scripts]
            index = (scriptnos.index(scriptno))
            video_scripts[index].status = status
            video_scripts[index].editedby = editedby
            if editedby is None:
                video_scripts[index].editedby = None

        except IndexError:
            print("couldn't find script %s" % scriptno)
