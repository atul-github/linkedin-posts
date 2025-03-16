import streamlit as st
from bs4 import BeautifulSoup

def render_post(post):
    soup = BeautifulSoup(post['postHtml'], "html.parser")
    st.markdown(str(soup), unsafe_allow_html=True)
    # Sample LinkedIn post in HTML
    # linkedin_post_html = f"<div style='border:1px solid #ccc; padding:10px; border-radius:5px;'><h3>{post['posterName']}</h3><p>{post['postHtml']}</div>"

    # # Sample comments
    # comments = [
    #     {"name": "Alice", "comment": "Congratulations, John! 🎉"},
    #     {"name": "Bob", "comment": "Wishing you all the best in your new role!"},
    #     {"name": "Charlie", "comment": "Looking forward to hearing about your journey!"},
    # ]


    st.markdown("### Comments")

    # Display comments in a chat-style UI
    for comment in post["comments"]:
        with st.chat_message("user"):
            soup = BeautifulSoup(comment['commentHtml'], "html.parser")
            st.markdown(f"**{comment['commenterName']}**:")
            st.markdown(str(soup), unsafe_allow_html=True)
            
            # st.markdown(f"**{comment['commenterName']}**: {comment['commentHtml']}")
