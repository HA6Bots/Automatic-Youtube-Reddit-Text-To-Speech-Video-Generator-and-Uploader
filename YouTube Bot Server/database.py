import mysql
import pickle
import hashlib
import mysql.connector
from mysql.connector import pooling
import settings
import datetime
from time import sleep

def initDatabase():
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("SET sql_notes = 0; ")
    cursor.execute("create database IF NOT EXISTS youtubebot")
    cursor.execute("USE youtubebot;")
    cursor.execute("SET sql_notes = 0; ")
    cursor.execute("set global max_allowed_packet=67108864;")

    cursor.execute("create table IF NOT EXISTS users (username varchar(70),password varchar(80), status varchar(80));")
    cursor.execute("create table IF NOT EXISTS videogenerators (generatorname varchar(70),password varchar(80), status varchar(80));")
    # youtube account, estimated length, actual length
    cursor.execute("create table IF NOT EXISTS scripts (scriptno int NOT NULL AUTO_INCREMENT, PRIMARY KEY (scriptno), submission_id varchar(70), subredditid varchar(70), subreddit varchar(70), url varchar(2083), timecreated DATETIME,"
                   "status varchar(70), editedby varchar(70), scripttitle varchar(2083), scriptauthor varchar(70), ups int, downs int, num_comments int, timegathered DATETIME, timeuploaded DATETIME, sceduledupload DATETIME, esttime time, actualtime time, rawscript MEDIUMBLOB, "
                   "finalscript MEDIUMBLOB);")
    cursor.execute("SET sql_notes = 1; ")

connection_pool = None

def login(username, password):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT count(*) FROM users WHERE username = %s AND password = %s;"%(repr(username), repr(password))

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection_object.close()
    flag = (result[0][0])
    if flag == 0:
        return False
    else:
        return True

def getScriptEditInformation():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT scriptno, status, editedby FROM scripts WHERE status = 'EDITING' AND editedby IS NOT NULL;"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)

    cursor.close()
    connection_object.close()
    return results

def completeUpload(scriptno, timeuploaded, scedualedrelease):
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "UPDATE scripts " \
            "SET status = 'SUCCESSUPLOAD', timeuploaded = %s, sceduledupload = %s WHERE scriptno = %s;"
    args = (timeuploaded, scedualedrelease, scriptno)
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def getLastUploadedScripts():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    now = datetime.datetime.now()
    cursor.execute("USE youtubebot;")
    query = "SELECT timeuploaded "\
            "from scripts "\
            "WHERE timeuploaded <= '%s' "\
            "ORDER BY timeuploaded DESC "\
            "LIMIT 6;" % (now.strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)
    cursor.close()
    connection_object.close()
    return results

def getCompletedScripts():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT scriptno, status, editedby FROM scripts WHERE status = 'COMPLETE' AND editedby IS NOT NULL;"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res)

    cursor.close()
    connection_object.close()
    return results

def getOnlineUsers():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT username FROM users WHERE status = 'ONLINE';"
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        results.append(res[0])

    cursor.close()
    connection_object.close()
    return results

def updateScriptStatus(status, user, scriptid):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    if user is None:
        user = "NULL"
    else:
        user = user
    cursor.execute("USE youtubebot;")
    query = "UPDATE scripts " \
            "SET status = %s, editedby = %s WHERE scriptno = %s;"
    args = (status, user, scriptid)

    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def updateScriptStatusById(status, user, scriptid):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    if user is None:
        user = "NULL"
    else:
        user = user
    cursor.execute("USE youtubebot;")
    query = "UPDATE scripts " \
            "SET status = %s, editedby = %s WHERE submission_id = %s;"
    args = (status, user, scriptid)

    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def updateUserStatus(user, status):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    if status is None:
        status = "NULL"
    else:
        status = repr(status)
    cursor.execute("USE youtubebot;")
    query = "UPDATE users " \
            "SET status = %s WHERE username = %s;"
    args = (status, user)

    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def getScriptStatus(scriptno):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT status " \
            "FROM scripts WHERE scriptno = %s;"%(scriptno)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection_object.close()
    return result[0][0]

def getScriptIds():
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT scriptno, submission_id, status " \
            "FROM scripts;"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection_object.close()
    return result


def getCompletedScripts(back):
    global connection_pool
    try:
        connection_object = connection_pool.get_connection()
        cursor = connection_object.cursor()
        cursor.execute("USE youtubebot;")

        query = "SELECT scriptno, scripttitle, scriptauthor, ups, finalscript " \
    "FROM scripts WHERE status = 'COMPLETE' AND finalscript IS NOT NULL ORDER BY ups DESC " \
    "LIMIT %s;"%back
        cursor.execute(query)
        result = cursor.fetchall()
        results = []
        for res in result:
            scriptno = res[0]
            scripttitle = res[1]
            author = res[2]
            ups = res[3]
            scriptpayload = pickle.loads(res[4])
            load = (scriptno, scriptpayload[9], author, ups, scriptpayload)
            results.append(load)
        cursor.close()
        connection_object.close()
        return results
    except Exception as e:
        print("Mysql Error with downloading completed scripts")
        print(e)
        pass

def getScripts(back, filter):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")

    query = "SELECT scriptno, subreddit, scripttitle, scriptauthor, ups, downs, rawscript, submission_id, status, editedby, num_comments " \
"FROM scripts WHERE status = 'RAW' or status = 'EDITING' ORDER BY %s DESC " \
"LIMIT %s;"%(filter, back)
    cursor.execute(query)
    result = cursor.fetchall()
    results = []
    for res in result:
        scriptno = res[0]
        subreddit = res[1]
        title = res[2]
        author = res[3]
        ups = res[4]
        downs = res[5]
        rawscript = pickle.loads(res[6])
        sub_id = res[7]
        status = res[8]
        editedby = res[9]
        num_comments = res[10]
        load = (scriptno, subreddit, title, author, ups, downs, rawscript, sub_id, status, editedby, num_comments)
        results.append(load)
    cursor.close()
    connection_object.close()
    return results

def addUser(username, password):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "INSERT INTO users(username, password) " \
            "VALUES(%s, %s)"
    args = (username, hashlib.md5(password.encode()).hexdigest())
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def addVideoGenerator(name, password):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    query = "INSERT INTO videogenerators(generatorname, password) " \
            "VALUES(%s, %s)"
    args = (name, hashlib.md5(password.encode()).hexdigest())
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def beginDataBaseConnection():
    global connection_pool
    connection_pool = pooling.MySQLConnectionPool(
    pool_size=32,
        pool_reset_session=True,
      host=settings.database_host,
      user=settings.database_user,
      passwd=settings.database_password,
    auth_plugin='mysql_native_password'
    )
    print("Started database connection")

def uploadVid(payload, scriptno):
    global connection_pool
    try:
        connection_object = connection_pool.get_connection()
        cursor = connection_object.cursor()
        cursor.execute("USE youtubebot;")
        cursor.execute("set global max_allowed_packet=67108864;")
        connection_object.commit()
        load = pickle.dumps(payload)
        print("%s SERVER attempting to upload script no %s (%s) to database" % (datetime.datetime.now(), scriptno, str((len(load) / 1000000)) + "MB"))
        query = "UPDATE scripts SET finalscript = %s WHERE scriptno = %s " \
                ""
        args = (load, scriptno)
        cursor.execute(query, args)
        connection_object.commit()
    except Exception as e:
        print("Error while connecting to MySQL using Connection pool ", e)
        return False
    finally:
        if (connection_object.is_connected()):
            cursor.close()
            connection_object.close()
        return True

def updateSubmission(submission):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    rawscript = pickle.dumps(submission.comments)
    query = "UPDATE scripts " \
            "SET scripttitle = %s, rawscript = %s, ups = %s, downs = %s, num_comments = %s, timecreated = %s, timegathered = %s WHERE submission_id = %s"
    args = (submission.title, (rawscript), submission.upvotes, submission.downvotes, submission.amountcomments,
            submission.timecreated, submission.timegathered, submission.submission_id)

    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def addSubmission(submission):
    global connection_pool
    connection_object = connection_pool.get_connection()
    cursor = connection_object.cursor()
    cursor.execute("USE youtubebot;")
    rawscript = pickle.dumps(submission.comments)
    query = "INSERT INTO scripts(subredditid, submission_id, subreddit, url, timecreated, status, scripttitle, scriptauthor, timegathered, rawscript, ups, downs, num_comments) " \
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    args = ((submission.subredditid), (submission.submission_id),
             (submission.subreddit), (submission.link), (submission.timecreated),
             ("RAW"), submission.title, (submission.author), (submission.timegathered), rawscript,
             submission.upvotes, submission.downvotes, submission.amountcomments)
    cursor.execute(query, args)
    connection_object.commit()
    cursor.close()
    connection_object.close()

def checkValueExists(column, value):
    global database
    cursor = database.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT count(*) FROM scripts WHERE %s = %s;"%(column, repr(value))
    cursor.execute(query)
    result = cursor.fetchall()
    flag = (result[0][0])
    if flag == 0:
        return False
    else:
        return True

def getVideoCountFromStatus(status):
    global database
    cursor = database.cursor()
    cursor.execute("USE youtubebot;")
    query = "SELECT count(*) FROM scripts WHERE status=%s;"%(repr(status))
    cursor.execute(query)
    result = cursor.fetchall()
    return (result[0][0])

def getRowCount(tablename):
    global database
    cursor = database.cursor()
    cursor.execute("USE youtubebot;")

    cursor.execute("select count(*) from %s"%tablename)
    result = cursor.fetchall()
    return (result[0][0])
