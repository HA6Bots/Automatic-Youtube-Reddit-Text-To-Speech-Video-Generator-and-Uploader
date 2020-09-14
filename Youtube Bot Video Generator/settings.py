import os, configparser
import platform

currentPath = os.path.dirname(os.path.realpath(__file__))

if platform == "win32":
    tempPath = (r"%s\\Temp" % currentPath)
    assetPath = (r"%s\\Assets" % currentPath)
    exportPath = (r"%s\\Export" % currentPath)
    overlayPath = (r"%s\\Overlay" % currentPath)
    videoqueue_directory = r"%s\\VIDEOQUEUE\\" % currentPath
    rawvideosaves = r"%s\\VIDEOQUEUE\\RAWSAVES" % currentPath
    finishedvideosdirectory = r"%s\\VIDEOQUEUE\\RENDEREDVIDS" % currentPath
    #google_cred = (r"%s\\Creds\\Royal Reddit Youtube-0c4b02452951.json" % currentPath)
    creds_path = r"%s\\Creds\\" % currentPath
    google_cred_upload = (r"%s\\Creds\\client_secrets.json" % currentPath)
    google_cred_upload_creds = (r"%s\\Creds\\.youtube-upload-credentials.json" % currentPath)
    google_tts_location = (r"%s\\Creds\\google-text-to-speech-credentials.json" % currentPath)

else:
    tempPath = ("%s/Temp" % currentPath)
    assetPath = ("%s/Assets" % currentPath)
    overlayPath = ("%s/Overlay" % currentPath)

    exportPath = ("%s/Export" % currentPath)
    videoqueue_directory = "%s/VIDEOQUEUE/" % currentPath
    rawvideosaves = "%s/VIDEOQUEUE/RAWSAVES" % currentPath
    finishedvideosdirectory = "%s/VIDEOQUEUE/RENDEREDVIDS" % currentPath
    creds_path = r"%s/Creds/" % currentPath
    #google_cred = ("%s/Creds/Royal Reddit Youtube-0c4b02452951.json" % currentPath)
    google_cred_upload = ("%s/Creds/client_secrets.json" % currentPath)
    google_cred_upload_creds = ("%s/Creds/.youtube-upload-credentials.json" % currentPath)
    google_tts_location = ("%s/Creds/google-text-to-speech-credentials.json" % currentPath)

print(google_cred_upload)

movieFPS = 30
exportOffline = False


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
noSpeech = False
offsetTextX = 0
offsetTextY = 20
# night-mode text color (215, 218, 220)
# night-mode background color (25, 25, 26)
comment_text_color = (215, 218, 220)
author_text_color = "#595959"
author_details_color = "#8CB9E6"

config = configparser.RawConfigParser()

server_address = "localhost"
server_port = 11000

use_balcon = True
use_google_tts = False
google_tts_language_code = 'en-US'
google_tts_voice = 'en-US-Wavenet-D'
voice_volume = 0.2
balcon_voice = "ScanSoft Daniel_Full_22kHz"
uploads_a_day = 6
background_music_volume = 0.2
random_upload_hour_boundary1 = 16
random_upload_hour_boundary2 = 18
youtube_api_quota_reset_hour = 8
balcon_location = "wine /home/royalreddit/Desktop/balcon/balcon.exe"
youtube_upload_location = ""
python27_location = ""
use_overlay = False
overlay_image = None

estWordPerMinute = 175

def generateConfigFile():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if not os.path.isfile("config.ini"):
        print("Couldn't find config.ini, creating new one")
        config.add_section("server_location")
        config.set("server_location", 'address', 'localhost')
        config.set("server_location", 'port_server', '10000')

        config.add_section("uploads")
        config.set("uploads", 'export_offline', 'False')
        config.set("uploads", 'fps', '60')
        config.set("uploads", 'uploads_a_day', '6')
        config.set("uploads", 'random_upload_hour_boundary1', '16')
        config.set("uploads", 'random_upload_hour_boundary2', '18')
        config.set("uploads", 'youtube_api_quota_reset_hour', '8')

        config.add_section("paths")
        config.set("paths", 'youtube_upload_location', '')
        config.set("paths", 'python27_location', '')

        config.add_section("balcon_tts")
        config.set("balcon_tts", 'use_balcon', 'true')
        config.set("balcon_tts", 'balcon_location_or_commandline', '')
        config.set("balcon_tts", 'balcon_voice', 'ScanSoft Daniel_Full_22kHz')

        config.add_section("google_tts")
        config.set("google_tts", 'use_google_tts', 'false')
        config.set("google_tts", 'google_tts_language_code', 'en-US')
        config.set("google_tts", 'google_tts_voice', 'en-US-Wavenet-D')

        config.add_section("other")
        config.set("other", 'background_music_volume', '0.2')
        config.set("other", 'voice_volume', '0.2')
        config.set("other", 'disable_speech', 'False')
        config.set("other", 'est_word_per_minute', '175')

        config.add_section("overlay")
        config.set("overlay", 'use_overlay', 'False')
        config.set("overlay", 'overlay_image', '')




        with open("config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config.ini")
        loadValues()

def loadValues():
    global server_address, server_port, uploads_a_day, random_upload_hour_boundary1,\
        random_upload_hour_boundary2, youtube_api_quota_reset_hour, balcon_location, youtube_upload_location,\
        python27_location, movieFPS, exportOffline, use_google_tts, balcon_voice, use_balcon, google_tts_language_code,\
        google_tts_voice, background_music_volume, voice_volume, noSpeech, estWordPerMinute, use_overlay, overlay_image
    config = configparser.RawConfigParser()

    config.read("config.ini")
    server_address = config.get('server_location', 'address')
    server_port = config.get('server_location', 'port_server')

    uploads_a_day = config.getint('uploads', 'uploads_a_day')
    movieFPS = config.getint('uploads', 'fps')
    exportOffline = config.getboolean('uploads', 'export_offline')
    random_upload_hour_boundary1 = config.getint('uploads', 'random_upload_hour_boundary1')
    random_upload_hour_boundary2 = config.getint('uploads', 'random_upload_hour_boundary2')
    youtube_api_quota_reset_hour = config.getint('uploads', 'youtube_api_quota_reset_hour')

    youtube_upload_location = config.get('paths', 'youtube_upload_location')
    python27_location = config.get('paths', 'python27_location')

    use_balcon = config.getboolean('balcon_tts', 'use_balcon')
    balcon_location = config.get('balcon_tts', 'balcon_location_or_commandline')
    balcon_voice = config.get('balcon_tts', 'balcon_voice')

    use_google_tts = config.getboolean('google_tts', 'use_google_tts')
    google_tts_language_code = config.get('google_tts', 'google_tts_language_code')
    google_tts_voice = config.get('google_tts', 'google_tts_voice')

    background_music_volume = config.getfloat('other', 'background_music_volume')
    voice_volume = config.getfloat('other', 'voice_volume')
    noSpeech = config.getboolean('other', 'disable_speech')
    estWordPerMinute = config.getint('other', 'est_word_per_minute')

    use_overlay = config.getboolean('overlay', 'use_overlay')
    overlay_image = config.get('overlay', 'overlay_image')



    if not os.path.exists(tempPath):
        print("Creating Temp Path: " + tempPath)
        os.makedirs(tempPath)
    else:
        print("Found Temp Path")

    if not os.path.exists(assetPath):
        print("Creating Assets Path: " + assetPath)
        os.makedirs(assetPath)
    else:
        print("Found Assets Path")

    if not os.path.exists("%s/Verdana.ttf" % assetPath):
        print("Missing assets please make sure you have all the correct assets: \n %s/Verdana.ttf" % assetPath)
    else:
        print("found Verdana.ttf")

