import pandas as pd
import numpy as np
def cleanup():
    pass


def just_url(urlWithParams):
    if (urlWithParams != None):
       return urlWithParams.split("?")[0]
    return ""


messages_array = []
mentions_array = []
def create_post_in_db(post, mentions):
    global messages_array
    global mentions_array
    try:
        poster = just_url(post["posterUrl"])
        postHtml = post.get("postHtml", "")
        id = len(messages_array) + 1
        post_id = id
        message = {
            "id" : id,
            "post_text" : postHtml,
            "create_url" : poster,
            "type": "post",
            "post_id" : post_id
        }
        messages_array.append(message)

        for comment in post.get("comments", []):
            commenter = comment["commenterUrl"]
            commenter = just_url(commenter)
            commentHtml = comment.get("commentHtml", "")
            id = len(messages_array) + 1
            message = {
                "id" : id,
                "post_text" : commentHtml,
                "create_url" : commenter,
                "type": "comment",
                "post_id" : post_id
            }        
            messages_array.append(message)

        if ( post.get("resharedContent", None) != None and post["resharedContent"].get("posterUrl", None) != None):
            reshare = post["resharedContent"]
            rposter = reshare["posterUrl"]
            rposter = just_url(rposter)
            rposterhtml = reshare["postHtml"]
            id = len(messages_array) + 1
            message = {
                "id" : id,
                "post_text" : rposterhtml,
                "create_url" : rposter,
                "type": "shared",
                "post_id" : post_id
            }        
            messages_array.append(message)            
        for mention in mentions:
            id = len(mentions_array) + 1
            mention = just_url(mention[0])
            new_mention = {
                "id" : id,
                "mention_url" : mention,
                "post_id" : post_id
            }
            mentions_array.append(new_mention)
    except Exception as e:
        print("Error : ",str(e))


def set_post_id():
    pass

def retrieve_common_post(url1, url2) :
    global messages_array
    global mentions_array

    try:
        if ( len(messages_array) == 0 and len(mentions_array) == 0 ):
            return
        mentions_df = pd.DataFrame(mentions_array) if mentions_array else pd.DataFrame(columns=["id", "mention_url", "post_id"])
        messages_df = pd.DataFrame(messages_array) if messages_array else pd.DataFrame(columns=["id", "post_text", "create_url", "type", "post_id"])
        

        mentions_url1 = mentions_df[mentions_df["mention_url"] == url1]["post_id"]
        mentions_url2 = mentions_df[mentions_df["mention_url"] == url2]["post_id"]

        common_mentions = set(mentions_url1) & set(mentions_url2)
        
        messages_url1 = messages_df[messages_df["create_url"] == url1]["post_id"]
        messages_url2 = messages_df[messages_df["create_url"] == url2]["post_id"]

        common_messages = set(messages_url1) & set(messages_url2)

        unique_post_ids = common_mentions | common_messages  # Union of both sets

        filtered_messages = messages_df[messages_df["post_id"].isin(unique_post_ids)]

        sorted_filtered_messages = filtered_messages.sort_values(by='id')
        posts = {}
        for index, message in sorted_filtered_messages.iterrows():
            post_type = message['type']
            if ( post_type == 'post') :
                posts[f"p_{message['id']}"] = {
                    "postHtml" : message['post_text'],
                    "posterUrl" : message['create_url'],
                    "comments" : [],
                    "resharedContent" : {}
                }
            elif (post_type == 'comment'):
                post = posts[f"p_{message['post_id']}"]
                comments = post["comments"]
                comments.append({
                    "comment" : message['post_text'],
                    "commenterUrl" : message['create_url']
                })
            elif (post_type == 'shared'):
                post = posts[f"p_{message['post_id']}"]
                resharedContent = post["resharedContent"]
                resharedContent["postHtml"] = message['post_text']
                resharedContent["posterUrl"] = message['create_url']             
            else:
                print("Error - this should not come...")
        return posts
    except Exception as e:
        print("Error:", e)  

if __name__ == "__main__":
  #insert_records()
  pass
  