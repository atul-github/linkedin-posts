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

    payload = {
        "model" : os.environ["OLLAMA_MODEL"],
        "stream": False,
        "prompt" : prompt,
          "options": {
            "temperature": 0.7
        }
    }
    return payload


async def execute(payload):
    url = os.environ["OLLAMA_URL"]
    headers = {'Content-Type': 'application/json'}
    try: 
        response_data = await make_async_request(url=url, headers=headers, payload=json.dumps(payload))
        response_json = response_data  
        return response_json["response"]
    except:
        return "Received error response from LLM"

# response = response = asyncio.run(llm.execute(payload)) # asyncio.run(make_async_request(url=antropicUrl, headers=headers, payload=json.dumps(build_llm_payload(prompt_template))))
# answer = response

