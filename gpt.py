import json
import os
import asyncio
import aiohttp
import os

async def make_async_request(url, headers, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload, proxy=os.getenv('https_proxy')) as response:
            response_data = await response.json()
            return response_data
        

def prepare_request(prompt):
    messages = []
    messages.append({
        "role": "user",
        "content": [{
            "type": "text",
            "text": prompt
        }]
    })    
    payload = {
    "messages": [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are an AI assistant who is an expert in analyzing contents of Linkedin posts to find out connectedness among people when they endorse each other or when they have established professional relationships."
                }
            ]
        }
    ] + messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }
    return payload


async def execute(payload):
    url = os.environ["URL"]
    api_key = os.environ["API_KEY"]
    headers = {'Content-Type': 'application/json', 'api-key': api_key}
    try:
        response_data = await make_async_request(url=url, headers=headers, payload=json.dumps(payload))
        response_json = response_data  
        return response_json["choices"][0]["message"]["content"]
    except:
        return "Received error response from LLM"

# response = response = asyncio.run(llm.execute(payload)) # asyncio.run(make_async_request(url=antropicUrl, headers=headers, payload=json.dumps(build_llm_payload(prompt_template))))
# answer = response

