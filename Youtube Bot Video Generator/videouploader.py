import os
from subprocess import *
import settings
import subprocess
import httplib2
import os
import sys

from oauth2client import client
import traceback
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client import file
youtube_bot_path = "I:\Python3.4.3\YouTubeBot\youtube-upload-master\\bin\\"



def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = settings.creds_path + ".youtube-upload-credentials.json"
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(settings.google_cred_upload, 'https://www.googleapis.com/auth/youtube.upload')
        flow.user_agent = 'youtube-upload'
        credentials = tools.run_flow(flow, store)
    return credentials


def upload(title, description, tags, thumbnailpath, filepath, time_to_upload):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    try:#checkcall
        p = subprocess.check_call([settings.python27_location,
                   "%s\\__main__.py" % settings.youtube_upload_location,
                   "--title=%s" % title,
                   "--description=%s" % description,
                   "--category=Entertainment",
                   "--thumbnail=%s"% thumbnailpath,
                   "--tags=%s" % tags,
                   #"--default-language=\"en\"",
                   #"--embeddable=True",
                   "--publish-at=%s" % time_to_upload,
                   "--privacy=private",
                   #"--default-audio-language=\"en\"",
                   "--credentials-file=%s" % settings.google_cred_upload_creds,
                   "--client-secrets=%s" % settings.google_cred_upload,
                   "%s" % filepath], stderr=STDOUT)

    except subprocess.CalledProcessError as e:
        print("Error Occured Uploading Video")
        if e.returncode == 3:
            print("Out of quotes")
        return False
        #print(output)
    # "--thumbnail=%s" % settings.upload_path + thumbnailpath,

    print("successfully finished uploading video")
    return True

"""
--title="A.S. Mutter" " \
  --description="A.S. Mutter plays Beethoven" \
  --category="Music" \
  --tags="mutter, beethoven" \
  --recording-date="2011-03-10T15:32:17.0Z" \
  --default-language="en" \
  --default-audio-language="en" \
  --client-secrets="my_client_secrets.json" \
  --credentials-file="my_credentials.json" \
  --playlist="My favorite music" \
  --embeddable=True|False \

--privacy (public | unlisted | private)  
--publish-at (YYYY-MM-DDThh:mm:ss.sZ)  
--location (latitude=VAL,longitude=VAL[,altitude=VAL])  
--thumbnail (string)  


"""