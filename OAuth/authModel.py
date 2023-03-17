import datetime
import math
import os
import json

# pip install psycopg2
import traceback

import psycopg2

# pip install -U python-dotenv
from dotenv import load_dotenv

load_dotenv()

# pip install pyjwt
import jwt

from authPayload import authPayload
from authResponse import authResponse

# Get environment variables
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv("DBPASSWORD")
AUTHSECRET = "dlksjgf"
EXPIRESSECONDS = 30000


def authenticate(clientId, clientSecret):
    conn = None
    encoded_jwt = ''
    query = "select * from passwords where login='" + clientId + "' and pass='" + clientSecret + "'"
    # sql = "INSERT INTO tokens VALUES ('" + clientId + "', '" + encoded_jwt +"', " + "now(), " + "now() + '"+ str(EXPIRESSECONDS) +" second', "+"now())"
    # print(query)
    try:
        conn = psycopg2.connect("dbname=" + "authdb" + " user=" + "postgres" + " password=" + "WiRe7301")
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        isAdmin = False
        # print(rows)
        # print("*^&&^*^&", cur.rowcount)
        if cur.rowcount == 1:
            if check_token(conn, clientId):
                # print(check_token(conn, clientId))
                cur.execute("DELETE FROM tokens WHERE login='" + clientId + "'")
                conn.commit()

            for row in rows:
                # print(row)
                isAdmin = False
                payload = authPayload(row[0], row[1], isAdmin)
                # print("ryqwqtyw",payload)
                break

            # print(payload.__dict__)
            encoded_jwt = jwt.encode(payload.__dict__, AUTHSECRET, algorithm='HS256')
            # print(encoded_jwt)
            response = authResponse(encoded_jwt, EXPIRESSECONDS, isAdmin)
            # print(response)
            sql = "INSERT INTO tokens VALUES ('" + clientId + "', '" + encoded_jwt + "', " + "now(), " + "now() + '" + str(
                EXPIRESSECONDS) + " second', " + "now())"
            cur.execute(sql)
            conn.commit()
            # print(time_check(encoded_jwt))
            # cur.close()
            # print(sql)
            # print(jwt.decode(encoded_jwt, AUTHSECRET, algorithms=['HS256']))
            return response.__dict__


        else:
            return False

    except (Exception, psycopg2.DatabaseError) as error:

        print(error)
        print(traceback.format_exc())

        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()


def time_check(token):
    token_time = jwt.decode(token, AUTHSECRET, algorithms=['HS256'])['exp']
    import time
    # print(math.trunc(time.time()), token_time)
    if math.trunc(time.time()) < float(token_time):
        return True
    return False


def check_token(conn, login):
    sql = "select * from tokens where login='" + login + "'"
    cur = conn.cursor()
    cur.execute(sql)
    # cur.fetchall()
    # print(cur.rowcount)
    if cur.rowcount == 1:
        return True
    return False


def verify(token):
    try:
        isBlacklisted = checkBlacklist(token)
        if isBlacklisted == True:
            return {"success": False}
        else:
            decoded = jwt.decode(token, AUTHSECRET, algorithms=['HS256'])
            return decoded
    except (Exception) as error:
        print(error)
        return {"success": False}


def create(clientId, clientSecret, isAdmin):
    conn = None
    query = "insert into clients (\"ClientId\", \"ClientSecret\", \"IsAdmin\") values(%s,%s,%s)"

    try:
        conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER + " password=" + DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query, (clientId, clientSecret, isAdmin))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()


def blacklist(token):
    conn = None
    query = "insert into blacklist (\"token\") values(\'" + token + "\')"
    try:
        conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER + " password=" + DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()


def checkBlacklist(token):
    conn = None
    query = "select count(*) from blacklist where token=\'" + token + "\'"
    print(query)
    try:
        conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER + " password=" + DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        if result[0] == 1:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            cur.close()
            conn.close()

        return True
    finally:
        if conn is not None:
            cur.close()
            conn.close()
