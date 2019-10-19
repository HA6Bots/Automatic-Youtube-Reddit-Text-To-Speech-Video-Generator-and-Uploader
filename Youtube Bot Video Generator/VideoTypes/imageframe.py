from moviepy.editor import *
from PIL import ImageFont, ImageDraw, Image
import random
from time import sleep
import settings
import random
import pandas
from subprocess import *
import subprocess
import re
import pickle
import matplotlib

# from google.cloud import texttospeech


"""
Install AVbin at https://avbin.github.io/AVbin/Download.html
Otherwise the audio reading module pyglet doesn't work


pyttsx3 instead of gtts as it offers multiple voices with different pitches and shit, gtts only gives you a female voice
need pywin32 for pyttsx3
"""


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
        self.audio_path2 = "%s/tempaudio%s.wav" % (settings.tempPath, frameno)
        self.audio_clip = None
        self.font = None
        self.duration = None  # duration of the motherfucking audio clip
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
        # gTTS audio clip
        # self.audio_clip = gTTS(text=self.text, lang=settings.language, slow=False)
        # with open(self.audio_path, 'wb') as fp:
        #    self.audio_clip.write_to_fp(fp

        print(self.text)
        print(repr(self.text))
        command = "wine /home/royalreddit/Desktop/balcon/balcon.exe -t \"%s\" -n ScanSoft Daniel_Full_22kHz -w '%s'" % (
        self.text, self.audio_path2)

        process = subprocess.call(command, shell=True)

        # "C:\Program Files (x86)\eSpeak\command_line\espeak.exe"
        # music = pyglet.media.load(self.audio_path2, streaming=False)
        # self.duration = music.duration
        # print("(%s)(%s)(TTS) %s" % (self.audio_path2, self.image_path, repr(self.text)))
        """
        try:
            self.audio_clip = AudioFileClip(self.audio_path2).fx(afx.volumex, 1.5)
            self.duration = self.audio_clip.duration
            print("(TTS) %s" % repr(self.text))
        except Exception as e:
            print("error converting text to speech: %s" % repr(self.text))
            self.audio_clip = None
            self.duration = 0.2
            return
        """
        # if "the audio is split" in self.text:
        #    self.audio_clip.preview()
        # https://github.com/pndurette/gTTS/issues/31 instructions on how to change the voice to male


"""
def textToSpeech(text, path):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Standard-B',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    with open(path, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file %s' % path)
    pass
"""


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


"""
Text to speech requirements:

Must be a male voice.
Must be able to export file.


Pytssx3
-you can change voice, pitch, gender,
-you can even sync word events as they are said
-it is offline so very quick
HOWEVER
-you cannot save the audio file

Gtts
-can save audio files
HOWEVER
-only one voice provided by google which is female
-can't change voice and speed
-online so not that quick

eSpeak
-can save audio files
-can change voice and speed
-offline so quick
HOWEVER
-can't sync word events
-have to use command line because official module (py-espeak-ng) is broken/buggy
http://espeak.sourceforge.net/commands.html

eSpeak Command Line options:

-a <integer>
    Sets amplitude (volume) in a range of 0 to 200. The default is 100.
-p <integer>
    Adjusts the pitch in a range of 0 to 99. The default is 50.
-s <integer>
    Sets the speed in words-per-minute (approximate values for the default English voice, others may differ slightly). 
    The default value is 175. I generally use a faster speed of 260. The lower limit is 80. 
    There is no upper limit, but about 500 is probably a practical maximum.
-g <integer>
    Word gap. This option inserts a pause between words. The value is the length of the pause, in units of 10 mS (at the default speed of 170 wpm).
-k <integer>
    Indicate words which begin with capital letters.
-l <integer>
    Line-break length, default value 0. If set, then lines which are shorter than this are treated as separate clauses 
    and spoken separately with a break between them. This can be useful for some text files, but bad for others.
-v <voice filename>[+<variant>]
    Sets a Voice for the speech, usually to select a language. eg:
-w <wave file>
    Writes the speech output to a file in WAV format, rather than speaking it.
--sep [=<character>]
    The character is used to separate individual phonemes in the output which is produced by the -x or --ipa options.
     The default is a space character. The character z means use a ZWNJ character (U+200c).
--split [=<minutes>]
    Used with -w, it starts a new WAV file every <minutes> minutes, at the next sentence boundary.
--voices [=<language code>]
    Lists the available voices.
    If =<language code> is present then only those voices which are suitable for that language are listed.
    --voices=mbrola lists the voices which use mbrola diphone voices. These are not included in the default --voices list
    --voices=variant lists the available voice variants (voice modifiers).


"""

"""
PYTTSX3
def getInstalledVoices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Voice:")
        print(" - ID: %s" % voice.id)
        print(" - Name: %s" % voice.name)
        print(" - Languages: %s" % voice.languages)
        print(" - Gender: %s" % voice.gender)
        print(" - Age: %s" % voice.age)

"""

"""
eSpeak
subprocess.call([settings.eSpeakPath, "-w" + settings.tempPath + "/file_name" + ".wav", text])


"""

