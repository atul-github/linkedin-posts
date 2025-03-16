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
proxy is required only when you are doing pip install behind corp firewall

```sh
$ git clone https://github.com/atul-github/linkedin-posts poc
$ cd poc
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip install --proxy=http://localhost:3128 -r requirements.txt

## only require if you are running behind firewall
$ export http_proxy=http://localhost:3128  
$ export https_proxy=http://localhost:3128 
```

# Environment Variables

Create .env file or add these variables. 

```
URL=https://<your url>/openai/deployments/<your deployment>/chat/completions?api-version=2024-02-15-preview
API_KEY=<your key>

OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:latest
```
If OLLAMA has higher preference. 

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

## Running d3js
You can see connections using d3js application as well.
Once streamlit application is up and running, you need to upload .jsonl file. Once file is uploaded successfully, you can run python httpserver

```sh
$ python -m http.server 8003
```

and browse to http://localhost:8003 

![alt text](image-1.png)



# Other experiments

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
