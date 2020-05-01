from datetime import timedelta
import os
import configparser

wordsPerMinute = 175 # avg is between 125-150, assuming 125 for now
timeBetweenCommentThread = timedelta(seconds=1)
recommendedLength = timedelta(minutes=10)
currentPath = os.path.dirname(os.path.realpath(__file__))

thumbnailpath = currentPath + "/Thumbnails"
scriptsaves = currentPath + "/Scriptsaves"
censorWords = False

config = configparser.ConfigParser()


server_address = "localhost"
server_port = "10000"

auto_login_user =  ""
auto_login_password = ""
darkMode = False
amount_scripts_download = 80

def generateConfigFile():
    path = "%s\\config.ini" % currentPath
    if not os.path.isfile(path):
        print("Could not find config file in location %s, creating a new one" % path)
        config.add_section("server_location")
        config.set("server_location", 'address', 'localhost')
        config.set("server_location", 'port', '10000')
        config.add_section("auto_login")
        config.set("auto_login", 'username', '')
        config.set("auto_login", 'password', '')
        config.add_section("other")
        config.set("other", 'amount_scripts', '80')
        config.set("other", 'censor_words', 'false')
        config.set("other", 'dark_mode', 'false')

        with open("%s\\config.ini" % currentPath, 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config in location %s" % path)
        loadValues()

def loadValues():
    global server_address, server_port, auto_login_password, auto_login_user, amount_scripts_download, censorWords, darkMode
    config = configparser.ConfigParser()
    config.read("%s\\config.ini" % currentPath)
    server_address = config.get('server_location', 'address')
    server_port = config.get('server_location', 'port')
    auto_login_user = config.get('auto_login', 'username')
    auto_login_password = config.get('auto_login', 'password')
    amount_scripts_download = config.getint('other', 'amount_scripts')
    censorWords = config.getboolean('other', 'censor_words')
    darkMode = config.getboolean('other', 'dark_mode')
