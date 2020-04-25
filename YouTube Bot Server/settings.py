import configparser, os

config = configparser.RawConfigParser()


server_location = "localhost"
server_port = "10000"
server_port_vid_gen = "11000"

reddit_client_id = ""
reddit_client_secret = ""
reddit_client_password = ""
reddit_client_user_agent = ""
reddit_client_username = ""
reddit_minimum_comments = 1000
reddit_comments_per_post = 30
reddit_replies_per_comment = 4
reddit_amount_posts = 45
music_types = ["Funny", "Sad", "Soothing"]

database_host = ""
database_user = ""
database_password = ""

def generateConfigFile():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if not os.path.isfile("config.ini"):
        print("Couldn't find config.ini, creating new one")
        config.add_section("server_location")
        config.set("server_location", 'address', 'localhost')
        config.set("server_location", 'port_server', '10000')
        config.set("server_location", 'port_vid_gen_server', '11000')
        config.add_section("reddit")
        config.set("reddit", 'client_id', '')
        config.set("reddit", 'client_secret', '')
        config.set("reddit", 'password', '')
        config.set("reddit", 'user_agent', 'RedditDATA')
        config.set("reddit", 'username', '')
        config.set("reddit", 'reddit_minimum_comments', 1000)
        config.set("reddit", 'reddit_comments_per_post', 30)
        config.set("reddit", 'reddit_replies_per_comment', 4)
        config.set("reddit", 'reddit_amount_posts', 45)


        config.add_section("database")
        config.set("database", 'host', '')
        config.set("database", 'user', '')
        config.set("database", 'password', '')

        config.add_section("videos")
        config.set("videos", 'musictypes', 'Funny, Sad, Soothing')


        with open("config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        print("Found config.ini")
        loadValues()

def loadValues():
    global server_location, server_port, server_port_vid_gen, reddit_client_id, reddit_client_secret,\
        reddit_client_password, reddit_client_user_agent, reddit_client_username, database_host,\
        database_user, database_password, reddit_minimum_comments, reddit_comments_per_post,\
        reddit_replies_per_comment, reddit_amount_posts, reddit_amount_posts, music_types
    config = configparser.RawConfigParser()

    config.read("config.ini")
    server_location = config.get('server_location', 'address')
    server_port = config.get('server_location', 'port_server')
    server_port_vid_gen = config.get('server_location', 'port_vid_gen_server')

    reddit_client_id = config.get('reddit', 'client_id')
    reddit_client_secret = config.get('reddit', 'client_secret')
    reddit_client_password = config.get('reddit', 'password')
    reddit_client_user_agent = config.get('reddit', 'user_agent')
    reddit_client_username = config.get('reddit', 'username')
    reddit_minimum_comments = config.getint('reddit', 'reddit_minimum_comments')
    reddit_replies_per_comment = config.getint('reddit', 'reddit_replies_per_comment')
    reddit_comments_per_post = config.getint('reddit', 'reddit_comments_per_post')
    reddit_amount_posts = config.getint('reddit', 'reddit_amount_posts')

    database_host = config.get('database', 'host')
    database_user = config.get('database', 'user')
    database_password = config.get('database', 'password')

    music_types = config.get('videos', 'musictypes').replace(" ", "").split(",")


