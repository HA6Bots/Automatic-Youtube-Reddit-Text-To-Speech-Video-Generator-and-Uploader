from abc import ABC, abstractmethod
import videosettings
from collections import namedtuple

class VideoFormat(ABC):

    def loadFormat(self, dictionary):
        self.settings = namedtuple('x', dictionary.keys())(*dictionary.values())

    @abstractmethod
    def stillImage(self, replies):
        pass

    @abstractmethod
    def calculateFontSize(self, replies, preferred_size=videosettings.preferred_font_size):
        pass
