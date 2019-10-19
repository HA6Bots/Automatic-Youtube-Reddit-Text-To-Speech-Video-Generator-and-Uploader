from abc import ABC, abstractmethod
import settings
from collections import namedtuple
import random

class VideoFormat(ABC):

    def loadSave(self):
        pass
        #save = scriptinput.loadJson(self.scriptsaveidentifier)
        #self.settings = namedtuple('x', save.keys())(*save.values())

    def loadFormat(self, dictionary):
        self.settings = namedtuple('x', dictionary.keys())(*dictionary.values())

    def selectMusic(self, musictype):
        if musictype == "funny":
            randInterval = random.randint(1, 38)
            self.music = ("%s/Music/Funny/funny%s.mp3" % (settings.assetPath, randInterval))

    @abstractmethod
    def stillImage(self, replies):
        pass

    @abstractmethod
    def stillImage(self, replies):
        pass

    @abstractmethod
    def calculateFontSize(self, replies, preferred_size=settings.preferred_font_size):
        pass

    @abstractmethod
    def renderClips(self, replies):
        pass

    @abstractmethod
    def createMovie(self, movie):
        pass