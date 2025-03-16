import json
import pandas as pd
from bs4 import BeautifulSoup
import networkx as nx
from collections import Counter
from bs4 import MarkupResemblesLocatorWarning
import warnings
# from titles_model import get_title_model
import os
# from pgutils import cleanup, create_post_in_db, set_post_id, retrieve_common_post
# from pandasutils import cleanup, create_post_in_db, set_post_id, retrieve_common_post
import pgutils
import pandasutils

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def cleanup():
   if ( os.environ.get("USE_PG", None) != None):
      return pgutils.cleanup()
   else:
      return pandasutils.cleanup()

def create_post_in_db(post, mentions):
   if ( os.environ.get("USE_PG", None) != None):
      return pgutils.create_post_in_db(post, mentions)
   else:
      return pandasutils.create_post_in_db(post, mentions)

def set_post_id():
   if ( os.environ.get("USE_PG", None) != None):
      return pgutils.set_post_id()
   else:
      return pandasutils.set_post_id()

def retrieve_common_post(url1, url2):
   if ( os.environ.get("USE_PG", None) != None):
      return pgutils.retrieve_common_post(url1, url2)
   else:
      return pandasutils.retrieve_common_post(url1, url2)

def just_url(urlWithParams):
    if (urlWithParams != None):
       return urlWithParams.split("?")[0]
    return ""

def extract_mentions(html):
    if ( html == None ):
       return []
    soup = BeautifulSoup(html, "html.parser")
    mentions = []
    for a in soup.find_all("a", href=True):
      if "linkedin.com/in/" in a["href"]:
          url = just_url(a["href"])
          name = a.text
          if(name == None or len(name) == 0):
             temp = url.split('/')
             name = temp[len(temp)-1]
          mentions.append((url, name))
      elif "linkedin.com/company/" in a["href"]:
          url = just_url(a["href"])
          name = a.text
          if(name == None or len(name) == 0):
             temp = url.split('/')
             name = temp[len(temp)-1]          
          mentions.append((url, name))
    # mentions = [a["href"] for a in soup.find_all("a", href=True) if "linkedin.com/in/" in a["href"]]
    return mentions

def get_common_posts(node1, node2):
   return retrieve_common_post(node1, node2)
   
   
def add_edge(G, m1, m2, weight, relation, m1_name=None, m1_title=None, m2_name=None, m2_title=None):
    if (G.has_edge(m1, m2)):
       if (G.edges[m1, m2]['mutual'] == 1):
          weight = weight * 2
       w = G.edges[m1, m2]["weight"]
       G.edges[m1, m2]["weight"] = w + weight
       r = G.edges[m1, m2][relation]
       G.edges[m1, m2][relation] = r + 1
    else:
      G.add_edge(m1, m2, weight=weight, **{"co-commented": 0, "mentioned": 0, "commented": 0, "mutual": 0, "shared": 0, "title_rank" : 0} )
      G.edges[m1, m2][relation] = 1
      if ( m1_name != None and len(m1_name) > 0):
        G.nodes[m1]["name"] = m1_name
      if ( m1_title != None and len(m1_title) > 0):
        G.nodes[m1]["title"] = m1_title            
        # title_rank_model = ()
        # rank = title_rank_model.predict([m1_title])[0]
        # G.edges[m1, m2]["title_rank"] = int(rank)
      if ( m2_name != None and len(m2_name) > 0):
        G.nodes[m2]["name"] = m2_name
      if ( m2_title != None and len(m2_title) > 0):
        G.nodes[m2]["title"] = m2_title

    if (G.has_edge(m2, m1)):
      if(G.edges[m2,m1]["mentioned"] > 0 and  G.edges[m2,m1]["commented"] > 0 and G.edges[m2,m1]["shared"] > 0):
        if ( G.edges[m2, m1]['mutual'] == 0):
          G.edges[m2, m1]['mutual'] = 1
          w = G.edges[m2, m1]['weight']
          G.edges[m2, m1]['weight'] = w * 2
        
        if (G.edges[m1, m2]['mutual'] == 0):
          G.edges[m1, m2]['mutual'] = 1
          w = G.edges[m1, m2]['weight']
          G.edges[m1, m2]['weight'] = w * 2

def search_nodes_by_name(G, name_to_search, max_search=100):
    query = name_to_search.lower() 
    searched_nodes = []
    i = 0
    for node, attrs in G.nodes(data=True):
        if "name" in attrs and attrs["name"].lower().startswith(query):
            i = i + 1
            if ( i > max_search ):
              break
            searched_nodes.append(node)

    return searched_nodes

def read_file(file):
  posts = []
  cleanup()
  flatten_posts = []
  G = nx.DiGraph()

  for i, line in enumerate(file):
    post_mentions = []
    post = json.loads(line.strip())
    mentions = extract_mentions(post["postHtml"])
    post["mentions"] = mentions
    poster = just_url(post["posterUrl"])
    posterName = post.get("posterName", "")
    post_mentions.extend(mentions)
    # poster_message_id = create_post_mentions(post["postHtml"], poster, mentions)

    for mention in mentions:
        add_edge(G, poster, mention[0], weight=1, relation="mentioned", m1_name=posterName,
                  m1_title=post.get("posterTitle", ""), m2_name=mention[1])

    if ( post.get("resharedContent", None) != None and post["resharedContent"].get("posterUrl", None) != None):
      reshare = post["resharedContent"]
      rposter = reshare["posterUrl"]
      rposter = just_url(rposter)
      rposterName = reshare.get("posterName", "")
      rposterhtml = reshare["postHtml"]
      rposterTitle = reshare.get("posterTitle", "")
      mentions = extract_mentions(rposterhtml)
      post_mentions.extend(mentions)

      for mention in mentions:
          add_edge(G, rposter, mention[0], weight=1, relation="mentioned", m1_name=rposterName,
                  m1_title=rposterTitle, m2_name=mention[1])
      
      add_edge(G, rposter, poster, weight=1, relation="shared", m1_name=rposterName,
              m1_title=rposterTitle, m2_name=posterName, m2_title=post.get("posterTitle", ""))


    for comment in post["comments"]:
        commenter = comment["commenterUrl"]
        commenter = just_url(commenter)
        comment_mentions = extract_mentions(comment["commentHtml"])
        post_mentions.extend(comment_mentions)
        for comment_mention in comment_mentions:
            add_edge(G, commenter, comment_mention[0], weight=1, relation="mentioned", 
                      m1_name=comment.get("commenterName", ""),
                      m1_title=comment.get("commenterTitle", ""),
                      m2_name=comment_mention[1]
                      )
        if ( commenter != poster ):
          # flatten_posts.append(flatten_post)
          add_edge(G, commenter, poster, weight=1, relation="commented",
                    m1_name=comment.get("commenterName", ""), m1_title=comment.get("commenterTitle", ""),
                    m2_name=post.get("posterName", ""), m2_title=post.get("posterTitle", "")
                    ) #"commented")
        if ( post.get("resharedContent", None) != None and post["resharedContent"].get("posterUrl", None) != None):
          add_edge(G, commenter, rposter, weight=0.2, relation="co-commented",
                    m1_name=comment.get("commenterName", ""), m1_title=comment.get("commenterTitle", ""),
                    m2_name=rposterName, m2_title=rposterTitle)
          add_edge(G, rposter, commenter, weight=0.2, relation="co-commented",
                    m1_name=rposterName, m1_title=rposterTitle,
                    m2_name=comment.get("commenterName", ""), m2_title=comment.get("commenterTitle", ""))           

    # Try to creation relationship between commenters with lower weights
    for i, comment1 in enumerate(post['comments']):
      for j, comment2 in enumerate(post['comments']):
        if ( j <= i ):
          continue
        commenter1 = comment1["commenterUrl"]
        commenter2 = comment2["commenterUrl"]
        commenter1 = just_url(commenter1)
        commenter2 = just_url(commenter2)
        if ( commenter1 != commenter2 ): 
          add_edge(G, commenter1, commenter2, weight=0.2, relation="co-commented",
                    m1_name=comment1.get("commenterName", ""), m1_title=comment1.get("commenterTitle", ""),
                    m2_name=comment2.get("commenterName", ""), m2_title=comment2.get("commenterTitle", ""))
          add_edge(G, commenter2, commenter1, weight=0.2, relation="co-commented")

    create_post_in_db(post, post_mentions)
    posts.append(post)
  # merged_df = df.groupby(['member1', 'member2']).apply(calculate_new_weight).reset_index()
  # df2 = update_relations_to_mutual(merged_df)

  # df2 = (merged_df['member1'] == merged_df['member2'].shift(1)) 
  #       & (merged_df['member2'] == merged_df['member1'].shift(1)) 
  #       & (merged_df['relation'].shift(1) == 'friend') & (merged_df['relation'] == 'colleague')

  # pd.set_option('display.max_columns', None)
  # print(df2)
  return G, posts


def initialize(upload_file):
  # G, posts, weights, df = read_file("./post_sample.jsonl/post_sample_small2.jsonl")
  G, posts = read_file(upload_file)
  set_post_id()
  # G, posts, df = read_file("./post_sample.jsonl/post_sample_small.jsonl")
  # G, posts, df = read_file("./post_sample.jsonl/post_sample.jsonl")     


  print("Number of nodes:", G.number_of_nodes())
  print("Number of edges:", G.number_of_edges())
  return G, posts
