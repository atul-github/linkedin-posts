# Introduction

This application can upload .jsonl file which consists of linkedin posts. It creates nodes for linkedin members and edges connecting nodes. It provides simple streamlit UI to play with.

# Install

## Python install

```sh
$ sudo apt install python3
$ sudo apt install python3-pip
$ sudo apt install python3.11-venv
```

## Project install

```sh
$ git clone https://github.com/atul-github/linkedin-posts poc
$ cd poc
$ python3 -m venv myenv
$ source myenv/bin/activate
```

When you are installing dependencies, please install individually. 


```
$ pip install pyvis beautifulsoup4 python-dotenv aiohttp networkx pandas streamlit psycopg2 numpy

```

# Environment Variables

Create .env file or add these variables. 

```
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:latest
```
If OLLAMA_URL is mentioned, application will use OLLAMA else it will fall back on GPT.
If you have GPT 4 access then 
```
URL=https://<your url>/openai/deployments/<your deployment>/chat/completions?api-version=2024-02-15-preview
API_KEY=<your key>
```

# Running streamlit application

## Run (without postgres)

```sh
$ python -m streamlit  run main.py --server.port=8002 --server.address=localhost --server.maxUploadSize=900
```

## Run (with postgres)

Add following in your environment variables or .env file

```
USE_PG=1
```
and run **pg.sql** to create two tables.

## Running d3js
You can see connections using d3js application as well.
Once streamlit application is up and running, you need to upload .jsonl file. Once file is uploaded successfully, you can run python httpserver

```sh
$ python -m http.server 8003
```

and browse to http://localhost:8003 

![alt text](image-1.png)



# Other experiments

Note that I had to download many add-ins separately because of network issues.

## Setiment analysis using spacytextblob

```sh
pip install spacy spacytextblob textblob torch
pip install ".\en_core_web_sm-3.8.0-py3-none-any.whl"
python spacytextblob_test.py
```

## Vader sentiment

```sh
pip install vaderSentiment
python vader_sentiment_test.py
```

## Benpar to find entities in text
```
pip install benepar
pip install .\en_core_web_trf-3.8.0-py3-none-any.whl
python benepar_test.py
```

## Title model for ranking
```
pip install scikit-learn
python titles_model.py
```

# Approach

* Upload .jsonl file
* Read each json object line by line
* Using **networkx** create nodes and edges . This is Directed graph.
* Create a node for every person who has posted, who has shared and who has commented on post.
* Create edges from commenter to poster, resharere to poster and then to mentions. So if commenter has mentioned someone, then edge will be created from commenter to mention.
* Weight is being calculated and 'mutual' relation is also calculated. This will be used while finding path between two nodes. This is used for only for display . I will work on it when I get chance or is required.

## Using LLM

**Pros**: Very accurate and limited to quality of prompt and token sizes.
**Cons**: Expensive and cannot prepopulate 'closeness' rank

## Training Model
* Create a dataset for linkedin post and rank it based on closeness
* Train model based on quality and quantiy of data (Fine-tune with RoBERTa, of using Transformer based model or simple TF-IDF Logistic Regression)
* Supply text from post to get 'closeness' rank that would classify relation between two people, for example Poster and Commenter
* I have attempted that with simple titles_model that would rank title.

**Pros** : Can train model with good amount of data / not expensive
**Cons** : Difficult to implement. Need to build dataset. Requires expertise. 

## Sentiment analysis

* Sentiment analysis using readymade models can give you decent results in terms of +ve or -ve tone

**Pros** : Easy to use.
**Cons** : Not accurate and cannot classify relation between two members





















