import os

currentPath = os.path.dirname(os.path.realpath(__file__))

exportPath = ("%s/Export" % currentPath)
assetPath = ("%s/Assets" % currentPath)
tempPath = ("%s/Temp" % currentPath)
eSpeakPath = ("I:\Python3.4.3\eSpeak\command_line\espeak.exe")
movieFPS = 50
language = "en-uk"


#1080p is 1920x1080
imageSize = (1920, 1080)
font_color = (0, 0, 0) #black
font_color_alpha = (0, 0, 0, 255)
punctuationList = [",","."]
characters_per_line = 125
offsetXReplyAmount = 30
reply_characters_factorX = 3
reply_fontsize_factorX = 0.625 #0.625
reply_fontsize_factorY = 1.15384
comment_author_factor = 0.9
offsetYReplyAmount = 30
thickness = 1
preferred_font_size = 30
offsetTextX = 0
offsetTextY = 20
# night-mode text color (215, 218, 220)
# night-mode background color (25, 25, 26)
comment_text_color = (215, 218, 220)
author_text_color = "#595959"
author_details_color = "#8CB9E6"
