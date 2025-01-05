import os
import base64
import httpx

from mistralai import Mistral
from dotenv import load_dotenv
from g4f.client import AsyncClient

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


async def image_recognition(image, text: str):
    image = encode_image_to_base64(image)
    api_key = os.getenv("AITOKEN")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "pixtral-12b-2409",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image}"}
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers=headers,
            json=data
        )

        response.raise_for_status()

        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "Извините, не удалось получить ответ от AI"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def image_generation(req):
    client = AsyncClient()
    api_key = os.getenv("AITOKEN")
    model = "ministral-3b-latest"

    client_text = Mistral(api_key=api_key)

    response = await client_text.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f'Улучши запрос для нейросети Flux, которая генерирует изображения, нужен английский язык, вот запрос: {req}',
            },
        ],
    )
    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    response = await client.images.generate(
        model='flux',
        prompt=full_response,
        response_format="b64_json"
    )

    return response.data[0].b64_json


