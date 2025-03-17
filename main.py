import networkx as nx
from bs4 import MarkupResemblesLocatorWarning
import warnings
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from graphutils import initialize, search_nodes_by_name, get_common_posts
#from neo4jutils import init_neo4j
from display_post import render_post
import dotenv
import csv
import json
import os
# from gpt import prepare_request
import gpt
import ollama
import asyncio


def llm_prepare_request(prompt):
    if ( os.environ.get("OLLAMA_URL", None) != None ):
      return ollama.prepare_request(prompt)
    else:
      return gpt.prepare_request(prompt)
    
def llm_execute(llm_payload):
    if ( os.environ.get("OLLAMA_URL", None) != None ):
      return asyncio.run(ollama.execute(llm_payload))
    else:
      return asyncio.run(gpt.execute(llm_payload))

dotenv.load_dotenv()
# from urllib.parse import urlparse, urlunparse
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

def search_node(key):
  min_chars = 1
  G = st.session_state.network
  if (key in st.session_state and len(st.session_state[key]) >= min_chars):
    if (key + "_saved" not in st.session_state ):
      st.session_state[key + "_saved"] = ""
    if ( st.session_state[key+"_saved"] != st.session_state[key] ):
      st.session_state[key+"_saved"] = st.session_state[key] 
      nodes = search_nodes_by_name(G, st.session_state[key])
      node_list = []
      for node in nodes:
        node_list.append((G.nodes[node]['name'], node))
      if ( key == "search_member1" ):
        st.session_state.search_nodes1 = node_list
      elif ( key == "search_member2" ):
        st.session_state.search_nodes2 = node_list
      else:
        st.session_state.search_nodes = node_list

def relation_message(node1, node2):
  G = st.session_state.network
  s = ""
  if (G.has_edge(node1, node2)):
      if ( G.edges[node1, node2]['commented'] > 0):
        s = f"<b>{G.nodes[node1]['name']}</b> has <b>commented</b> on {G.nodes[node2]['name']}</b>'s posts {G.edges[node1, node2]['commented']} time(s)"
      if ( G.edges[node1, node2]['mentioned'] > 0):
        s += f"{s}<br /><b>{G.nodes[node1]['name']}</b> has <b>mentioned</b> {G.nodes[node2]['name']}</b> {G.edges[node1, node2]['mentioned']} time(s)"
      if ( G.edges[node1, node2]['co-commented'] > 0):
        s += f"{s}<br /><b>{G.nodes[node1]['name']}</b> has <b>co-commented</b> with {G.nodes[node2]['name']}</b> {G.edges[node1, node2]['co-commented']} time(s)"
      if ( G.edges[node1, node2]['shared'] > 0):
        s += f"{s}<br /><b>{G.nodes[node1]['name']}</b> has <b>reshared</b> {G.nodes[node2]['name']}</b> post(s) {G.edges[node1, node2]['shared']} time(s)"
      return s
  else:
    return (f"There is no direction connection between <b>{G.nodes[node1]['name']}</b> and <b>{G.nodes[node2]['name']}</b>")

def find_relationship():
  G = st.session_state.network  
  c1, c2 = st.columns([4, 4], gap="small")
  with c1:
    st.text_input("Search Member 1", "", placeholder="Search linkedin member 1", key="search_member1", on_change=search_node("search_member1"))

    if ( "search_nodes1" in st.session_state ):
      if ( len(st.session_state.search_nodes1) == 0 ):
        st.write("No matching records found")
      else:
        st.selectbox(
                    "Select a member",
                    options=st.session_state.search_nodes1,
                    format_func=lambda x: x[0],
                    key='selected_node1',
                )

  with c2:
    st.text_input("Search Member 2", "", placeholder="Search linkedin member 2", key="search_member2", on_change=search_node("search_member2"))
    if ( "search_nodes2" in st.session_state ):
      if ( len(st.session_state.search_nodes2) == 0 ):
        st.write("No matching records found")
      else :
        st.selectbox(
                    "Select a member",
                    options=st.session_state.search_nodes2,
                    format_func=lambda x: x[0],
                    key='selected_node2',
                )     
        
  col1, col2, col3 = st.columns([4, 4, 4], gap="small")
  with col1:
    st.write("Click on Submit to check for direct connection")
    if st.button("Submit"):
      if ( "selected_node1" in st.session_state and "selected_node2" in st.session_state ):
        node1 = st.session_state.selected_node1[1]
        node2 = st.session_state.selected_node2[1]
        r_msg1 = relation_message(node1, node2)
        r_msg2 = relation_message(node2, node1)
        r_msg = r_msg1 + "<br />" + r_msg2
        if(G.has_edge(node1, node2) and G.has_edge(node2, node1)):
            if ( G.edges[node1, node2]['mutual'] > 0 ):
                r_msg += f"<br />They have <b>Mutual</b> relation. That means they are familiar with each other."
            else:
                r_msg += f"<br />They have commented on same posts. They are not familiar with each other<br />"
        if(not G.has_edge(node1, node2) and not G.has_edge(node2, node1)):
          exchange = get_common_posts(node1, node2)
          post_items = []
          for key, value in exchange.items():
              post_items.append(value)
              print(f"Property: {key}, Value: {value}")        
          if ( len(post_items) > 0 ):
            r_msg += "<br />" + f"Even if there is no direct relation exists, they were mentioned together in {len(post_items)} post(s)"
        st.session_state.relation_message = r_msg

    if ("relation_message" in st.session_state and len(st.session_state.relation_message) > 0 ):
      st.write(st.session_state.relation_message, unsafe_allow_html=True)
  with col2:
    st.write("Click on Path to check if selected members are connected")
    if st.button("Connection Path"):
      if ( "selected_node1" in st.session_state and "selected_node2" in st.session_state ):
        node1 = st.session_state.selected_node1[1]
        node2 = st.session_state.selected_node2[1]
        if (G.has_edge(node1, node2)):
          st.write("There is direct relation exists")
        def weight_fun(u, v, d):
          return 1 / d['weight']
          # relation_scores = {
          #   "mutual": 1,        # Strongest relation (smallest weight)
          #   "commented": 10,
          #   "mentioned": 10,
          #   "co-commenter" : 10,
          # }
          return relation_scores.get(d["relation"], 10)
        try: 
          path = nx.shortest_path(G, source=node1, target=node2, weight=weight_fun)
        except Exception as e:
          st.error(f"Error encountered - {str(e)}")
          path = None
        if ( path != None and len(path) < 2 ):
          st.write("No known path exists")
          path = None

        st.session_state.connectedness = path
  with col3:
    st.write("Click here to analyze relation using LLM")
    if st.button("Excecute LLM"):
      node1 = st.session_state.selected_node1[1]
      node2 = st.session_state.selected_node2[1]
      exchange = get_common_posts(node1, node2)
      post_items = []
      for key, value in exchange.items():
          post_items.append(value)
          print(f"Property: {key}, Value: {value}")        
      formatted_json_string = json.dumps(post_items, indent=4)
      prompt = f"""
          Below are linkedin post(s) and comments on post which is basically exchange between [{G.nodes[node1]['name']}]({node1}) and [{G.nodes[node2]['name']}]({node2}).

          ```json
          {formatted_json_string}
          ```

          Your task is to analyze post(s) and comment(s) and find out how strongly {G.nodes[node1]['name']} and {G.nodes[node2]['name']} connected.

          You can classify their relation as
          - They have frequently interacted
          - They are familiar with each other
          - They are close colleagues
          - They are not that much connected

          and human readable explanation why you classified their relation as one of above.

          In response, send me JSON object like below
          
          ```json
          {{
            "relation_classified" : <one of the above or something else you find>,
            "explanation" : <brief your explanation on why you classified this way>
          }}
        
          ```
      """

      llm_payload = llm_prepare_request(prompt)
      llm_resp = llm_execute(llm_payload)
      st.write(llm_resp)

      # llm_payload = gpt.prepare_request(prompt)
      # llm_resp = asyncio.run(gpt.execute(llm_payload))
      # st.write(llm_resp)
      # print(llm_payload)

      # llm_payload = ollama.prepare_request(prompt)
      # llm_resp = asyncio.run(ollama.execute(llm_payload))
      # st.write(llm_resp)
      #print(llm_resp)


        # path = nx.bellman_ford_path(G, source=node1, target=node2, weight=weight_fun)
        # st.write(path)



  if "connectedness" in st.session_state and st.session_state.connectedness != None:
    path_graph = nx.DiGraph()
    path = st.session_state.connectedness
    for u, v in zip(path, st.session_state.connectedness[1:]):  
      weight = G[u][v]["weight"]
      # print(weight)
      path_graph.add_edge(G.nodes[u]['name'], G.nodes[v]['name'], weight=weight)
    net = Network(directed=True, height="500px", width="100%", bgcolor="#222222", font_color="white")
    for u, v, d in path_graph.edges(data=True):
        net.add_node(u, label=u, color="cyan")
        net.add_node(v, label=v, color="cyan")
        #print(d["weight"])
        net.add_edge(u, v, label=str(d["weight"]), color="red")
    net.save_graph("path_graph.html")
    st.components.v1.html(open("path_graph.html", "r").read(), height=550, scrolling=False) 

def explore_node():
    G = st.session_state.network  
    st.text_input("Search Member", "", placeholder="Search linkedin member", key="search_member", on_change=search_node("search_member"))
    if ( "search_nodes" in st.session_state ):
      if ( len(st.session_state.search_nodes) == 0 ):
        st.write("No matching records found")
      else :
        st.selectbox(
                    "Select a member",
                    options=st.session_state.search_nodes,
                    format_func=lambda x: x[0],
                    key='selected_node',
                )
    if ( "selected_node" in st.session_state ) :
      node = st.session_state.selected_node[1]
      neighbors = set(G.predecessors(node)) | set(G.successors(node)) | {node}
      subgraph = G.subgraph(neighbors)
      net = Network(notebook=False, directed=True, height="600px", width="100%") #height="500px", width="100%", bgcolor="#222222", font_color="white"
      for n, attrs in subgraph.nodes(data=True):
        net.add_node(n, label=attrs.get("name", str(n)), size=5, font={"size": 5}) 
      for src, dst, attrs in subgraph.edges(data=True):
        net.add_edge(src, dst, label=str(attrs.get("weight", 0)), font={"size": 5})  
        options = """
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -3000,
              "centralGravity": 0.2,
              "springLength": 150,
              "springConstant": 0.01,
              "damping": 0.09
            },
            "minVelocity": 0.75
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.5
              }
            },
            "width": 0.5
          },
          "nodes": {
            "font": {
              "size": 8
            }
          }
        }
        """        
      net.set_options(options)        
      net.save_graph("explore_node.html")
      st.components.v1.html(open("explore_node.html", "r").read(), height=550, scrolling=False) 

def neo4j_playground():
  pass

def display_post():
  render_post(st.session_state.posts[0])

def upload_file():
    uploaded_file = st.file_uploader("Select .jsonl")
    if uploaded_file is not None:
      try:   
        G, posts = initialize(upload_file=uploaded_file)
        st.session_state.network = G
        st.session_state.posts = posts

        G = st.session_state.network

        # for node in G.nodes(data=True):
        #   print(node)
        
        with open("nodes.csv", mode='w', newline='', encoding='utf-8') as csv_file:
          csv_writer = csv.writer(csv_file)
          # csv_writer.writerow(["member1", "member1_name", "member1_title", "member2", "member2_name", "member2_title"])
          csv_writer.writerow(["id", "name", "title"])
          for node in G.nodes(data=True):
            try:
              csv_writer.writerow([node[0], node[1]['name'], node[1].get('title', "")])
            except Exception:
              print(node)

        with open("edges.csv", mode='w', newline='', encoding='utf-8') as csv_file:
          csv_writer = csv.writer(csv_file)
          csv_writer.writerow(["source", "target", "weight", "co-commented", "mentioned", "commented", "mutual", "shared", "title_rank"])
          for u, v, data in G.edges(data=True):
            csv_writer.writerow([u, v, data["weight"], data["co-commented"], data["mentioned"], 
                                 data["commented"], data["mutual"], data["shared"], data["title_rank"]])

        # print("\n\n---->\n\n")
        # for u, v, data in G.edges(data=True):
        #   print(f"Edge ({u}, {v}) with properties: {data}")
        
        # for node in G.nodes(data=True):
        #   print(node)
        # print("\n\n---->\n\n")
        st.rerun()

      except Exception as exp:
          st.error("Invalid JSON file" + str(exp))


def start_streamlit():
  st.set_page_config(page_title="Linkedin fun POC", layout="wide")
  st.title("Linkedin fun POC")

  if ("network" not in st.session_state ) :
    upload_file()
    return
  
  G = st.session_state.network


  radio = st.radio(
      "Select tab",
      ["Find relationship", "Explore", "Show post"],
      key="radio_tabs",
      label_visibility="collapsed",
      horizontal=True
  )    

  if (radio == "Find relationship"):
    find_relationship()
  elif (radio == "Explore"):
    explore_node()
  else:
    display_post()

if __name__ == "__main__":
  if "network" not in st.session_state:
    # G = initialize("./post_sample.jsonl/post_sample_very_small2.jsonl")
    # G = initialize("./post_sample.jsonl/post_sample.jsonl")
    # G = initialize("./post_sample.jsonl/test1.jsonl")
    # G = initialize("./post_sample.jsonl/test2.jsonl")
    # G, posts = initialize("./post_sample.jsonl/test3.jsonl")
    # G, posts = initialize("./post_sample.jsonl/test.jsonl")
    # init_neo4j(G)
    # G = initialize("./post_sample.jsonl/test3.jsonl")
    # st.session_state.network = G
    # st.session_state.posts = posts
    pass
  start_streamlit()
    
