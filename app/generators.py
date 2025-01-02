import os

import asyncio
import aiohttp
import aiofiles
import base64

from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()


async def text_generation(req):
    api_key = os.getenv("AITOKEN")
    model = "ministral-3b-latest"

    client = Mistral(api_key=api_key)

    response = await client.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "user",
                "content": req,
            },
        ],
    )
    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    return full_response if full_response else "Ошибка: пустой ответ от AI"


async def image_generation(req):
    pass


async def code_generation(req):
    api_key = os.getenv("AITOKEN")
    model = "codestral-2405"

    client = Mistral(api_key=api_key)

    response = await client.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "user",
                "content": req,
            },
        ],
    )
    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    return full_response if full_response else "Ошибка: пустой ответ от AI"


async def image_recognition(req):
    pass


"""
async def image_generation(req):
    api_key = os.getenv("AITOKEN")
    model = "pixtral-large"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': model,
        'prompt': req
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("AITOKEN", headers=headers, json=data) as response:
            if response.status == 200:
                response_data = await response.json()
                image_url = response_data.get('image_url')
                if image_url:
                    return image_url
                else:
                    return "Ошибка: пустой ответ от AI"
            else:
                return "Ошибка при выполнении запроса к API"

async def image_encode(image_path):
        async with aiofiles.open(image_path, "rb") as image_file:
            return base64.b64encode(await image_file.read()).decode('utf-8')
"""
"""
async def image_recognition(req, file):
    base64_image = await encode_image(file)

    headers = {
         "Content-Type": "application/json",
         "Authorization": f"Bearer {'AITOKEN'}"
    }
    payload = {
    "model": "gpt-4o-mini",
    "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    }

    if req is not None: 
         payload['messages'][0]['content'].append ({
                        "type": "text",
                        "text": req        
                    })


    async with aiohttp.ClientSession() as session:
         async with session.post("https://tripfixers.com/wp-content/uploads/2019/11/eiffel-tower-with-snow.jpeg", headers=headers, json=payload) as response:
              completion = await response.json()
    return {'response': completion['choices'][0]['message']['content'],
            'usage': completion['usage']['total_tokens']}
"""
