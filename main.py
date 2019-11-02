from InstagramAPI import InstagramAPI
import json, requests, sqlite3

DB_NAME ='db.db'

try:
    with sqlite3.connect(DB_NAME) as conn:
 
        cur = conn.cursor()
        #People who followed you after you followed them or people who are following you while you are following them
        cur.execute("""
        CREATE TABLE IF NOT EXISTS followed(
            parentid TEXT,
            parent TEXT,
            id TEXT UNIQUE,
            username TEXT UNIQUE
        );""")
        #People to Follow These people will be extract from random profiles 
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tofollow(
            parentid TEXT,
            parent TEXT,
            id TEXT UNIQUE,
            username TEXT UNIQUE
        );""")
        #FOllOWERS TREE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tree(
            parentid TEXT,
            parent TEXT,
            id TEXT UNIQUE,
            username TEXT UNIQUE
        );""")
        #People you have followed and they didn't follow back are here to not follow them again
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notfollow(
            parentid TEXT,
            parent TEXT,
            id TEXT UNIQUE,
            username TEXT UNIQUE
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS everyone(
            parentid TEXT,
            parent TEXT,
            id TEXT UNIQUE,
            username TEXT UNIQUE
        );
        """)

except Exception as e:
    print(e)

def get_id(username):
	url = "https://www.instagram.com/web/search/topsearch/?context=blended&query="+username+"&rank_token=0.3953592318270893&count=1"
	response = requests.get(url)
	respJSON = response.json()
	try:
		user_id = str( respJSON['users'][0].get("user").get("pk") )
		return user_id
	except:
		return "Unexpected error"



api = InstagramAPI("enjieldeeb@yahoo.com", "ahmedahmed")
api.login()
own_id = api.username_id
followers = api.getTotalFollowers(str(own_id))
with sqlite3.connect(DB_NAME) as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM followingyou")
    record = cur.fetchall()
    if len(record) == 0:
        for i in followers:
           
            cur.execute("INSERT OR IGNORE INTO followingyou (parentid,parent,id,username) VALUES(?,?,?,?)",(own_id,api.username,i['pk'],i['username']))
            cur.execute("INSERT OR IGNORE INTO tree (parentid,parent,id,username) VALUES(?,?,?,?)",(own_id,api.username,i['pk'],i['username']))
            cur.execute("INSERT OR IGNORE INTO everyone (parentid,parent,id,username) VALUES(?,?,?,?)",(own_id,api.username,i['pk'],i['username']))

    target = input("Enter User to Extract his followers or .txt file to with a list :")
    if target == "tree":
        cur.execute("SELECT id,username FROM everyone")
        record = cur.fetchall()
        cur2 = conn.cursor()
        counter = 0
        for i in record:
            if counter ==100:
                break
            counter+=1
            target_id = i[0]
            target_user = i[1]
            try:
                followers = api.getTotalFollowers(target_id)   
            except Exception as e:
                    if "big_list" in str(e):
                        pass         
            for j in followers:
                    cur2.execute("INSERT OR IGNORE INTO tree(parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target_user,j['pk'],j['username']))

                


    elif '.txt' in target:
        cur2 = conn.cursor()
        target_list = []
        file = open(target,"r")
        x = file.readlines()

        for i in x:
            target_list.append(i.replace("\n",""))

        for target_user in target_list:
            target_id = get_id(str(target_user))
            try:
                followers = api.getTotalFollowers(target_id)

                for i in followers:
                    
                    cur2.execute("INSERT OR IGNORE INTO tofollow (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target_user,i['pk'],i['username']))          
                    cur2.execute("INSERT OR IGNORE INTO everyone (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target_user,i['pk'],i['username']))
                    cur2.execute("INSERT OR IGNORE INTO tree (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target_user,i['pk'],i['username']))

            except Exception as e:
                if "big_list" in str(e):
                    print(target_user,"is a private account.")

    
    else:
        target_id = get_id(str(target))
        try:
            followers = api.getTotalFollowers(target_id)
        except Exception as e:
            if "big_list" in str(e):
                print(target,"is a private account.")
        
        for i in followers:
           
            cur.execute("INSERT OR IGNORE INTO tofollow (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target,i['pk'],i['username']))
            cur.execute("INSERT OR IGNORE INTO everyone (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,target,i['pk'],i['username']))
            cur.execute("INSERT OR IGNORE INTO tree (parentid,parent,id,username) VALUES(?,?,?,?)",(target_id,api.username,i['pk'],i['username']))














"""
api = InstagramAPI("enjieldeeb@yahoo.com", "ahmedahmed")
api.login()

own_id = api.username_id

followers = api.getTotalFollowers(get_id("ahmedezzatpy"))
print('Number of followers:', len(followers))

check = input("Do you Want to List Followers(y/n): ")
    if str(check).lower() =="y":
    for i in followers:
        print("Name: "+i['full_name'],"Username: "+i['username'])
"""
