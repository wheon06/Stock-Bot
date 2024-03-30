import sqlite3
import discord


def checkUser(user_id):
    alr_exist = []
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT user_id FROM UserInfo WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()

    for i in rows:
        alr_exist.append(i[0])

    if user_id not in alr_exist:
        return 0

    elif user_id in alr_exist:
        return 1

    con.close()


def checkBank(user_id):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT bank FROM UserInfo WHERE user_id = ?", (user_id,))
    bank = cur.fetchall()

    if bank[0][0] == 'NULL':
        return 0

    elif bank[0][0] != 'NULL':
        return 1

    con.close()

def getIdIndex(user_id):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(user_id) FROM UserInfo")
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    cur.execute("SELECT user_id FROM UserInfo")
    user_id_tuple = cur.fetchall()
    temp1 = []
    temp2 = []

    for i in range(userLenInt):
        temp1.append(list(user_id_tuple[i]))
        temp2.append(temp1[i][0])

    user_ids = temp2
    index = user_ids.index(user_id)
    con.close
    return index


def getValueOnDB(user_id, value, table):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT " + value + " FROM " + table)
    value_buf = cur.fetchall()
    cur.execute("SELECT COUNT(" + value + ") FROM " + table)
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    con.close()
    value_list = []
    for i in range(userLenInt):
        value_list.append(list(value_buf[i]))

    value2 = value_list[getIdIndex(user_id)]
    value1 = value2[0]
    return value1


def getStockCount():
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(stock_id) FROM Stock")
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    con.close()
    return userLenInt


def getStockOnDB(stock_id, value, table):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(stock_id) FROM " + table)
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    cur.execute("SELECT stock_id FROM " + table)
    stock_id_tuple = cur.fetchall()
    temp1 = []
    temp2 = []

    for i in range(userLenInt):
        temp1.append(list(stock_id_tuple[i]))
        temp2.append(temp1[i][0])

    stock_ids = temp2
    index = stock_ids.index(stock_id)

    cur.execute("SELECT " + value + " FROM " + table)
    value_buf = cur.fetchall()
    cur.execute("SELECT COUNT(" + value + ") FROM " + table)
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    con.close()

    value_list = []
    for i in range(userLenInt):
        value_list.append(list(value_buf[i]))

    value2 = value_list[index]
    value1 = value2[0]
    return value1


def getStockPriceOnDB(stock_name, value, table):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(stock_name) FROM " + table)
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    cur.execute("SELECT stock_name FROM " + table)
    stock_name_tuple = cur.fetchall()
    temp1 = []
    temp2 = []

    for i in range(userLenInt):
        temp1.append(list(stock_name_tuple[i]))
        temp2.append(temp1[i][0])

    stock_names = temp2
    try:
        index = stock_names.index(stock_name)
    except:
        return 0

    cur.execute("SELECT " + value + " FROM " + table)
    value_buf = cur.fetchall()
    cur.execute("SELECT COUNT(" + value + ") FROM " + table)
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    con.close()

    value_list = []
    for i in range(userLenInt):
        value_list.append(list(value_buf[i]))

    value2 = value_list[index]
    value1 = value2[0]
    return value1


def stockNameCheck(name):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(stock_name) FROM Stock")
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    cur.execute("SELECT stock_name FROM Stock")
    stock_name_tuple = cur.fetchall()
    temp1 = []
    temp2 = []

    for i in range(userLenInt):
        temp1.append(list(stock_name_tuple[i]))
        temp2.append(temp1[i][0])

    stock_names = temp2
    try:
        index = stock_names.index(name)
        return 1
    except:
        return 0