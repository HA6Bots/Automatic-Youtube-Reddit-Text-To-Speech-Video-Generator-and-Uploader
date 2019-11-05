import os, configparser
import platform

currentPath = os.path.dirname(os.path.realpath(__file__))

if platform == "win32":
    tempPath = (r"%s\\Temp" % currentPath)
    assetPath = (r"%s\\Assets" % currentPath)
    exportPath = (r"%s\\Export" % currentPath)
    videoqueue_directory = r"%s\\VIDEOQUEUE\\" % currentPath
    rawvideosaves = r"%s\\VIDEOQUEUE\\RAWSAVES" % currentPath
    finishedvideosdirectory = r"%s\\VIDEOQUEUE\\RENDEREDVIDS" % currentPath
    #google_cred = (r"%s\\Creds\\Royal Reddit Youtube-0c4b02452951.json" % currentPath)
    creds_path = r"%s\\Creds\\" % currentPath
    google_cred_upload = (r"%s\\Creds\\client_secrets.json" % currentPath)
    google_cred_upload_creds = (r"%s\\Creds\\.youtube-upload-credentials.json" % currentPath)

else:
    tempPath = ("%s/Temp" % currentPath)
    assetPath = ("%s/Assets" % currentPath)
    exportPath = ("%s/Export" % currentPath)
    videoqueue_directory = "%s/VIDEOQUEUE/" % currentPath
    rawvideosaves = "%s/VIDEOQUEUE/RAWSAVES" % currentPath
    finishedvideosdirectory = "%s/VIDEOQUEUE/RENDEREDVIDS" % currentPath
    creds_path = r"%s/Creds/" % currentPath
    #google_cred = ("%s/Creds/Royal Reddit Youtube-0c4b02452951.json" % currentPath)
    google_cred_upload = ("%s/Creds/client_secrets.json" % currentPath)
    google_cred_upload_creds = ("%s/Creds/.youtube-upload-credentials.json" % currentPath)


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

uploads_a_day = 6
random_upload_hour_boundary1 = 16
random_upload_hour_boundary2 = 18
youtube_api_quota_reset_hour = 8
balcon_location = "wine /home/royalreddit/Desktop/balcon/balcon.exe"
youtube_upload_location = ""
python27_location = ""

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
        config.set("paths", 'balcon_location', '')
        config.set("paths", 'youtube_location', '')
        config.set("paths", 'python27_location', '')



        with open("config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config.ini")
        loadValues()

def loadValues():
    global server_address, server_port, uploads_a_day, random_upload_hour_boundary1,\
        random_upload_hour_boundary2, youtube_api_quota_reset_hour, balcon_location, youtube_upload_location,\
        python27_location, movieFPS, exportOffline
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

    balcon_location = config.get('paths', 'balcon_location')
    youtube_upload_location = config.get('paths', 'youtube_location')
    python27_location = config.get('paths', 'python27_location')



