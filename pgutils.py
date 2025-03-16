import psycopg2
import json

DB_PARAMS = {
    "dbname": "mydb",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def cleanup():
    try: 
        conn = psycopg2.connect(
            dbname='mydb',
            user="postgres",
            password='postgres',
            host="localhost",
            port = "5432"
        
        )
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE messages RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE mentions RESTART IDENTITY CASCADE")
            conn.commit()        

    except Exception as e:
        print("Error:", e)  

connection  = None

def get_connection():
    try:
        global connection
        if (connection != None):
            return connection        
        connection = psycopg2.connect(
            dbname='mydb',
            user="postgres",
            password='postgres',
            host="localhost",
            port = "5432"
        )
        return connection
    except Exception as e:
        print("Error: ", str(e))


def create_post_in_db(post, mentions):
    try:
        conn = get_connection()

        poster = just_url(post["posterUrl"])
        postHtml = post.get("postHtml", "")

        with conn.cursor() as cursor:
            cursor.execute("insert into messages (post_text, create_url, type) values(%s, %s, %s)  RETURNING id", 
                            (postHtml, poster, 'post'))
            post_id = cursor.fetchone()[0] 
            for comment in post.get("comments", []):
                commenter = comment["commenterUrl"]
                commenter = just_url(commenter)
                commentHtml = comment.get("commentHtml", "")
                cursor.execute("insert into messages (post_text, create_url, type, post_id) values(%s, %s, %s, %s)  RETURNING id", 
                                (commentHtml, commenter, 'comment', post_id))    
            if ( post.get("resharedContent", None) != None and post["resharedContent"].get("posterUrl", None) != None):
                reshare = post["resharedContent"]
                rposter = reshare["posterUrl"]
                rposter = just_url(rposter)
                rposterhtml = reshare["postHtml"]
                cursor.execute("insert into messages (post_text, create_url, type, post_id) values(%s, %s, %s, %s)  RETURNING id", 
                                (rposterhtml, rposter, 'shared', post_id))
            for mention in mentions:
                mention = just_url(mention[0])
                cursor.execute("insert into mentions ( mention_url, post_id ) values(%s, %s )  RETURNING id", 
                                (mention, post_id))
            conn.commit()
    except Exception as e:
        print("Error : ",str(e))


def set_post_id():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            returned_value = cur.execute("update messages set post_id = id where post_id is null and type ='post'")
            conn.commit()
    except Exception as e:
        print("Error : ", str(e))

def retrieve_common_post(source, target) :
    try:
        conn = psycopg2.connect(
            dbname='mydb',
            user="postgres",
            password='postgres',
            host="localhost",
            port = "5432"
        )
        posts = {}
        with conn.cursor() as cur:
            cur.execute(f"""SELECT * FROM messages WHERE post_id IN ( 
                            SELECT distinct post_id FROM mentions WHERE mention_url = %s 
                                and post_id in (SELECT distinct post_id FROM mentions WHERE  mention_url = %s)
                            union 
                                SELECT distinct post_id from messages where create_url = %s and post_id in 
                                (SELECT distinct post_id from messages where create_url = %s )
                            )
                            order by id
                        """,(source, target, source, target))
            # cur.execute("SELECT * from messages WHERE id in ( SELECT distinct post_id FROM message_map WHERE source_url = %s and target_url = %s )", (source, target))
            rows = cur.fetchall()
            for row in rows:
                post_type  = row[3]
                if ( post_type == 'post'):
                    posts[f"p_{row[0]}"] = {
                        "postHtml" : row[1],
                        "posterUrl" : row[2],
                        "comments" : [],
                        "resharedContent" : {}
                    }
                elif ( post_type == 'comment'):
                    post = posts[f"p_{row[4]}"]
                    comments = post["comments"]
                    comments.append({
                        "comment" : row[1],
                        "commenterUrl" : row[2]
                    })
                elif ( post_type == 'shared'):
                    post = posts[f"p_{row[4]}"]
                    resharedContent = post["resharedContent"]
                    resharedContent["postHtml"] = row[1]
                    resharedContent["posterUrl"] = row[2]
                else:
                    print("Error - this should not come...")
            return posts
    except Exception as e:
        print("Error:", e)  


    

def create_map(source, target, message_id, action, post_id):
    try: 
        # conn = psycopg2.connect(
        #     dbname='mydb',
        #     user="postgres",
        #     password='postgres',
        #     host="localhost",
        #     port = "5432"
        # )
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("insert into message_map ( source_url, target_url, message_id, post_id, action) values(%s, %s, %s, %s, %s)  RETURNING id", 
                            (source, target, message_id, post_id, action))
        conn.commit()
    except Exception as e:
        print("Error:", e)  

def commented_together(source, target, post_id):
    try: 
        # conn = psycopg2.connect(
        #     dbname='mydb',
        #     user="postgres",
        #     password='postgres',
        #     host="localhost",
        #     port = "5432"
        
        # )
        conn = get_connection()
        with conn.cursor() as cursor:
            target = just_url(target)
            cursor.execute("insert into message_map ( source_url, target_url, post_id, action) values(%s, %s, %s, %s)  RETURNING id", 
                            (source, target, post_id, 'co-commented'))
            cursor.execute("insert into message_map ( source_url, target_url, post_id, action) values(%s, %s, %s, %s)  RETURNING id", 
                            (target, source, post_id, 'co-commented'))
            conn.commit()
    except Exception as e:
        print("Error:", e)  


def create_post_mentions(message, poster, mentions):
    try: 
        # conn = psycopg2.connect(
        #     dbname='mydb',
        #     user="postgres",
        #     password='postgres',
        #     host="localhost",
        #     port = "5432"
        
        # )
        conn = get_connection()
        source = just_url(poster)
        with conn.cursor() as cursor:
            cursor.execute("insert into messages (post_text, create_url, type) values(%s, %s, %s)  RETURNING id", 
                            (message, source, 'post'))
            inserted_id = cursor.fetchone()[0] 
            for i, target in enumerate(mentions):
                target = just_url(target[0])
                cursor.execute("insert into message_map ( source_url, target_url, post_id, message_id, action) values(%s, %s, %s, %s, %s)  RETURNING id", 
                                (source, target, inserted_id, inserted_id, 'mentioned'))
            # conn.commit()
        return inserted_id
    except Exception as e:
        print("Error:", e)  


def create_reshare_mentions(message, resharer, mentions, post_id):
    try: 
        # conn = psycopg2.connect(
        #     dbname='mydb',
        #     user="postgres",
        #     password='postgres',
        #     host="localhost",
        #     port = "5432"
        # )
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("insert into messages (post_text, create_url, type, post_id) values(%s, %s, %s, %s)  RETURNING id", 
                            (message, resharer, 'shared', post_id))
            inserted_id = cursor.fetchone()[0] 
            for i, target in enumerate(mentions):
                target = just_url(target[0])
                cursor.execute("insert into message_map ( source_url, target_url, message_id, post_id, action) values(%s, %s, %s, %s, %s)  RETURNING id", 
                                (resharer, target, inserted_id, post_id, 'mentioned'))
            # conn.commit()
        return inserted_id
    except Exception as e:
        print("Error:", e)  

def create_comment_mentions(message, commenter, mentions, post_id):
    try: 
        # conn = psycopg2.connect(
        #     dbname='mydb',
        #     user="postgres",
        #     password='postgres',
        #     host="localhost",
        #     port = "5432"
        # )
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("insert into messages (post_text, create_url, type, post_id) values(%s, %s, %s, %s)  RETURNING id", 
                            (message, commenter, 'comment', post_id))
            inserted_id = cursor.fetchone()[0] 
            for i, target in enumerate(mentions):
                target = just_url(target[0])
                cursor.execute("insert into message_map ( source_url, target_url, message_id, post_id, action) values(%s, %s, %s, %s, %s)  RETURNING id", 
                                (commenter, target, inserted_id, post_id, 'commented'))
            conn.commit()
        return inserted_id
    except Exception as e:
        print("Error:", e)  

def just_url(urlWithParams):
    if (urlWithParams != None):
       return urlWithParams.split("?")[0]
    return ""



def read_records():
  
  
  try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname='mydb',
        user="postgres",
        password='postgres',
        host="localhost",
        port = "5432"
    
    )
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM comments")
        rows = cur.fetchall()
        i = 0
        for row in rows:
            #print(f"ID: {row[0]}, poster_url: {row[1]}, poster_name: {row[2]}, poster_title: {row[3]}")
            title = row[4]
            if ( len(title) > 0 ):
                rank = model.predict([title])
                print(title, rank)

  except Exception as e:
      print("Error:", e)  


def insert_records():

  try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname='mydb',
        user="postgres",
        password='postgres',
        host="localhost",
        port = "5432"
    
    )


    with conn.cursor() as cursor:
        with open("./post_sample.jsonl/post_sample.jsonl", "r", encoding="utf-8") as file:
            batch_size = 100  # Commit after 100 inserts
            count = 0            
            for line in file:
                count += 1
                post = json.loads(line.strip())
                cursor.execute("insert into posts ( poster_url, poster_name, poster_title, post_html) values(%s, %s, %s, %s)  RETURNING post_id", 
                               (just_url(post["posterUrl"]), 
                                post.get("posterName", ""),
                                post.get("posterTitle", ""),
                                post.get("postHtml", ""),
                                ))
                inserted_id = cursor.fetchone()[0] 

                for comment in post["comments"]:
                    commenter = comment["commenterUrl"]
                    commenter = just_url(commenter)
                    cursor.execute("insert into comments ( post_id, commenter_url, commenter_name, commenter_title, comment_html) values(%s, %s, %s, %s, %s)", 
                                (
                                   inserted_id,
                                   comment.get("commenter_url", ""), 
                                    comment.get("commenterName", ""),
                                    comment.get("commenterTitle", ""),
                                    comment.get("commentHtml", ""),
                                ))


                if count % batch_size == 0:
                    conn.commit()
                    print(f"Committed {count} records...") 
            
            conn.commit()
        print("Records inserted successfully.")

  except Exception as e:
      print("Error:", e)  

if __name__ == "__main__":
  #insert_records()
  read_records()



  