# Introduction

This application allows you to upload a .jsonl file containing LinkedIn posts. It creates nodes for LinkedIn members and edges to connect them. A simple Streamlit UI is provided to interact with the application.

# Install


## Python install
First, install the required Python version and dependencies:

```sh
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3.11-venv
```

## Project install
Clone the repository and set up a virtual environment:

```sh
git clone https://github.com/atul-github/linkedin-posts poc
cd poc
python3 -m venv myenv
source myenv/bin/activate
```

Next, install the project dependencies:

```
sudo apt-get install libpq-dev python3.11-dev
pip install pyvis beautifulsoup4 python-dotenv aiohttp networkx pandas streamlit psycopg2 numpy

```
Please donot use requirements.txt as it may take very long time.


# Environment Variables
Create a .env file or add the following environment variables:

```
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:latest
```
If OLLAMA_URL is set, the application will use OLLAMA. Otherwise, it will default to GPT. 
If you have access to GPT-4, set the following:
```
URL=https://<your url>/openai/deployments/<your deployment>/chat/completions?api-version=2024-02-15-preview
API_KEY=<your key>
```

# Running streamlit application

## Run (without postgres)

```sh
python -m streamlit  run main.py --server.port=8002 --server.address=localhost --server.maxUploadSize=900
```

## Run (with postgres)

To run with PostgreSQL, add the following to your environment variables or .env file:

```
USE_PG=1
```
Please run **pg.sql** to create two tables.


## Running d3js
To visualize connections using a D3.js application, follow these steps:

Start the Streamlit application and upload the .jsonl file.
    Once the file is successfully uploaded, run the Python HTTP server:

    
```sh
python -m http.server 8003
```

and browse to http://localhost:8003/d3.html 

![alt text](image-1.png)

# Using App

* When launched for the first time, you will be prompted to upload .jsonl file
* It may take couple of minutes to upload the file :(
* You can search linkedin members. So if you type 'a', around 100 linkedin members will be populated in dropdown beneath. You will need to click outside of text box for search to start.
* Click 'Submit' - This will give you information if there is direct relation.
* Click Connectedness - It will give directed path between two memebers if available.
* Execute LLM - will do classification

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
* For **weight calculation** : few things i have implemented like weight is higher for 'mutual' relation. It should consider with whom you are connected. I will enhance this part little bit further

## Using LLM

**Pros**: 
Very accurate and limited to quality of prompt and token sizes.
Dependent on the quality of the prompt and token sizes.

**Cons**: 
Expensive
Cannot prepopulate the 'closeness' rank.


## Training Model
* Create a dataset of LinkedIn posts and rank them based on "closeness".
* Train a model using the data (fine-tune with RoBERTa or use a Transformer-based model or simple TF-IDF Logistic Regression).
* Supply text from posts to get a 'closeness' rank, which classifies the relationship between two people (e.g., Poster and Commenter).
* I attempted this with a simple title model to rank titles.

**Pros** : 
Can train model large dataset

**Cons** : 
* Need to create good quality dataset.
* Requires expertise. 

## Sentiment analysis

* Sentiment analysis using readymade models can give you decent results in terms of +ve or -ve tone. Sentiment value along with data, we can find out relative closeness between two members.

**Pros** : 
Easy to use.

**Cons** : 
Not accurate and cannot classify relation between two members





















