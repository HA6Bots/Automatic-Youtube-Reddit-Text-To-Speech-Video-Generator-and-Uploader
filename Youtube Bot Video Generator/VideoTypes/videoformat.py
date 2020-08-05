from abc import ABC, abstractmethod
import settings
from collections import namedtuple
import os
import random

class VideoFormat(ABC):

    def loadSave(self):
        pass
        #save = scriptinput.loadJson(self.scriptsaveidentifier)
        #self.settings = namedtuple('x', save.keys())(*save.values())

    def loadFormat(self, dictionary):
        self.settings = namedtuple('x', dictionary.keys())(*dictionary.values())

    def selectMusic(self, musictype):
        self.music = "%s/Music/%s/%s" % (settings.assetPath, musictype, random.choice(os.listdir("%s/Music/%s/" % (settings.assetPath, musictype))))

        while "DS_Store" in self.music:
            self.music = "%s/Music/%s/%s" % (settings.assetPath, musictype, random.choice(os.listdir("%s/Music/%s/" % (settings.assetPath, musictype))))


        print(self.music)

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
