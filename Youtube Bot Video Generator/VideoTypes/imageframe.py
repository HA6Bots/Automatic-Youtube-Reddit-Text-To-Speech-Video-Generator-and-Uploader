from moviepy.editor import *
from PIL import ImageFont, ImageDraw, Image
import random
from time import sleep
import settings
import random
import pandas
import platform
from subprocess import *
import subprocess
import re
from pydub import AudioSegment

import pickle
import matplotlib
import settings

# from google.cloud import texttospeech
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=settings.google_tts_location
from google.cloud import texttospeech





def deleteAllFilesInPath(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def parseScript(rawscript):
    newscript = []
    for x, commentThread in enumerate(rawscript):
        comment_to_append = ()
        for y, comment in enumerate(commentThread):
            comment_to_append = comment_to_append + (
                CommentWrapper(comment[0], comment[1], comment[2]),)
        newscript.append(comment_to_append)
    return newscript


class Frame():
    def __init__(self, image, text, frameno):
        self.text = text
        self.image_path = "%s/tempframe%s.png" % (settings.tempPath, frameno)
        self.audio_path = "%s/tempaudio%s.mp3" % (settings.tempPath, frameno)
        if platform == "win32":
            self.audio_path2 = "\"%s\"\\tempaudio%s.wav" % (settings.tempPath, frameno)
        else:
            self.audio_path2 = "%s/tempaudio%s.wav" % (settings.tempPath, frameno)
        self.audio_clip = None
        self.font = None
        self.duration = None
        self.generateAudioClip()
        self.saveClip(image)
        self.setFont()

    def setFont(self):
        fontpath = ("%s/Verdana.ttf" % (settings.assetPath))
        self.font = ImageFont.truetype(fontpath, 32)

    def getFont(self):
        return self.font

    def saveClip(self, clip):
        matplotlib.image.imsave(self.image_path, clip)

    def generateAudioClip(self):

        self.text = self.text.replace("<NL>", "")
        self.text = self.text.replace("\"", "'")
        if self.text == ".":
            self.text = " "
        elif self.text == "":
            self.text = " "
        self.text = self.text.replace("*", " ")
        self.text = self.text.replace("\"", " ")
        self.text = self.text.replace("\n", " ")

        #if not using google tts use balcon as default
        if not settings.noSpeech:
            if settings.use_google_tts:
                client = texttospeech.TextToSpeechClient()

                synthesis_input = texttospeech.types.SynthesisInput(text=self.text)

                voice = texttospeech.types.VoiceSelectionParams(
                    language_code=settings.google_tts_language_code,
                    name=settings.google_tts_voice,
                    ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

                audio_config = texttospeech.types.AudioConfig(
                    audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16)

                response = client.synthesize_speech(synthesis_input, voice, audio_config)

                with open(self.audio_path2, 'wb') as out:
                    out.write(response.audio_content)

            if settings.use_balcon:
                command = "%s -t \"%s\" -n %s -w %s" % (settings.balcon_location,
                self.text, settings.balcon_voice, "\"" + self.audio_path2 + "\"")

                process = subprocess.call(command, shell=True)
        else:
            amount_spaces = self.text.count(' ')
            estimated_time = ((amount_spaces / settings.estWordPerMinute) * 60) * 1000
            new_audio = AudioSegment.silent(duration=(estimated_time))
            new_audio.export(self.audio_path2, format='wav')




class VideoScript():
    def __init__(self, inputString):
        self.inputString = inputString

    def insertLineWrappingTags(self, characters=settings.characters_per_line):
        end = []
        textToAppend = ""
        for i, char in enumerate(repr(self.inputString)):
            textToAppend += char  # official string
            if "\\n" in textToAppend:
                end.append(textToAppend)
                textToAppend = ""

            if len(textToAppend) % characters == 0 and not i == 0:
                if not repr(self.inputString)[i + 1] == " ":
                    indWords = textToAppend.split(" ")
                    lastWord = indWords[len(indWords) - 1]
                    textToAppend = textToAppend[0:len(textToAppend) - len(lastWord):]
                    if not textToAppend == "":
                        end.append(textToAppend)
                    textToAppend = lastWord
                else:
                    if not textToAppend == "":
                        end.append(textToAppend)
                    textToAppend = ""

        characterAmount = 0
        for char in end:
            characterAmount += len(char)

        final_line = repr(self.inputString)[characterAmount:len(repr(self.inputString))]
        end.append(final_line)

        output = ""
        for i, line in enumerate(end):
            if i == len(end) - 1:
                line = line.replace("\\n", "")
                line = line[0: len(line) - 1]  # removes the ' at the end of the string on the last line
                output += line
                # print(len(line))
                # print(line)
                break
            if i == 0:
                pass
                # line = line[1: len(line)] # removes the ' at the start of the string on the first line
            line = line.replace("\\n", "")
            # print(len(line))
            # print(line)
            output += line + "<LW>"
        output = output[1: len(output)]
        self.inputString = output

    def insertNewLineTags(self):
        self.inputString = self.inputString.replace("\\n", "<NL>")

    def insertAudioBreakTags(self, puncList=settings.punctuationList):
        for char in puncList:
            self.inputString = self.inputString.replace(str(char), "%s<BRK>" % (str(char)))

    def getTags(self):

        output = []
        tags = ["<BRK>", "<NL>", "<LW>"]

        splt_str = re.split("(" + "|".join(tags) + ")", self.inputString)

        for i in range(0, len(splt_str), 2):
            output.append("".join(splt_str[i:i + 2]))

        parsedOutput = []
        for line in output:
            for tag in tags:
                if tag in line:
                    parsedOutput.append((line.replace(tag, ""), tag))

        parsedOutput.append((output[len(output) - 1], ""))
        return parsedOutput


def redditPointsFormat(input, includePoints=False):
    output = input
    if input >= 1000:
        output = str(round((input / 1000), 1))
        output = output.replace(".0", "")
        output += "k"
        if includePoints:
            output += " points"
    else:
        output = str(output) + ""
        if includePoints:
            output += " points"
    return output


class CommentWrapper():
    def __init__(self, author, text, upvotes, subcomments=None):
        self.author = author
        self.text = text
        self.upvotes = upvotes
        self.subcomments = subcomments


class CommentThread():
    def __init__(self, frames):
        self.frames = frames


