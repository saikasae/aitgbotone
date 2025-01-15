import base64
import io
import logging
import os
import duckduckgo_search
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from g4f.client import AsyncClient
from mistralai import Mistral
import matplotlib.pyplot as plt

load_dotenv()
logger = logging.getLogger(__name__)


def latex_to_image(latex_code):
    latex_code = latex_code.strip('$')

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

    fig, ax = plt.subplots(figsize=(15, 2))
    ax.text(0.05, 0.5, f'${latex_code}$', fontsize=14)
    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode('utf-8')


async def text_generation(req):
    api_key = os.getenv("AITOKEN")
    model = "mistral-large-2411"

    system_prompt = """
You are a highly skilled assistant specializing in solving mathematical problems and presenting solutions **exclusively in LaTeX format**. Your task is to generate correct and concise LaTeX code that accurately corresponds to the user's request.

**Mandatory Requirements:**

1. **LaTeX Only:** If a user asks you to solve a mathematical problem, equation, or simplify a mathematical expression, your response must contain **only** LaTeX code, without any additional text, explanations, introductions, or conclusions. No comments are allowed.
2. **Correct Syntax:** The generated LaTeX code must be absolutely correct and must not contain any syntax errors.
3. **Mathematical Mode:** All mathematical content must be enclosed in dollar signs (`$...$`).
    *   Use single dollar signs for inline formulas: `$...$`.
    *   Use double dollar signs for display-style formulas (on a separate line): `$$...$$`.
4. **No Extra Symbols:** Do not add any extra characters to the LaTeX code that are not related to the mathematical expression, such as:
    *   `\.` (a command that has no meaning in math mode)
    *   `\spacefactor` (a low-level TeX command not intended for direct use)
    *   `\\\\,` (incorrect use of line breaks and commas in math mode)
5. **Correct Use of Environments:** Use LaTeX environments (`\begin{}`, `\end{}`) only where necessary according to the syntax (e.g., for matrices, systems of equations, etc.). Do not use environments unnecessarily.
6. **Correct Line Breaks:** Use `\\\\` for line breaks **only outside** of math mode, if formatting requires it. Inside math mode (`$...$`), line breaks are not needed.
7. **Separation Symbols:** Remember to separate parts of the expression with `$\\,$`.
8. **Clear Adherence to the Request:** Carefully analyze the user's request and generate LaTeX code that precisely corresponds to the task.

**Examples of Correct LaTeX:**

*   Solving a quadratic equation: `$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$`
*   Derivative of a function: `$$\frac{d}{dx}(x^2 + 2x + 1) = 2x + 2$$`
*   Integral: `$$\int_{a}^{b} x^2 dx = \frac{b^3 - a^3}{3}$$`
*   Matrix: `$$\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$$`
*   System of equations: `$$\begin{cases} x + y = 5 \\ x - y = 1 \end{cases}$$`

**Examples of INCORRECT LaTeX:**

*   `\frac{d}{dx}(2 + 2) = 0 \.` (extra command `\.`)
*   `$\\\frac{d}{dx}(2 + 2) = 0 \\\\,$` (extra `\\\\,`)
*   `$$\begin{array}{c} \frac{x}{2} + \frac{y}{3} = 1 \end{array}$$` (unnecessary use of the `array` environment)
*   Solution: `$\frac{1}{2}$` (text "Solution:" is present, which is unacceptable)
*   ```latex
    x^2 + y^2 = z^2
    ``` (No need for code blocks)

**If the user's request is not mathematical or does not imply calculations in LaTeX, respond as a regular assistant.**

**Important:** This prompt aims to generate only LaTeX code for mathematical expressions. Your task is to strictly follow the instructions and not add anything extra.
The following code must be able to create an image based on your prompt; MiKTeX is used:

```python
def latex_to_image(latex_code):
    latex_code = latex_code.strip('$')

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    fig, ax = plt.subplots(figsize=(15, 2))
    ax.text(0.05, 0.5, f'${latex_code}$', fontsize=16)
    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode('utf-8')
    """

    req.insert(0,
    {
        "role": "system",
        "content": system_prompt
    })
    client = Mistral(api_key=api_key)

    response = await client.chat.stream_async(
        model=model,
        messages=req
    )

    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    if is_latex(full_response):
        print('Содержит LaTex')
        try:
            image_bytes = latex_to_image(full_response)
            return {"text": full_response, "image": image_bytes}
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения LaTeX: {e}")
            return {"text": full_response, "image": None}
    else:
        print('Не содержит LaTex')
        return {"text": full_response, "image": None}


def is_latex(text):
    latex_indicators = [
        "$",
        "\\frac",
        "\\int",
        "\\sum",
        "\\sqrt",
        "^",
        "_",
        "\\left",
        "\\right",
        "\\begin",
        "\\end",
    ]

    return sum(indicator in text for indicator in latex_indicators) >= 2

async def image_generation(req):
    client = AsyncClient()
    api_key = os.getenv("AITOKEN")
    model = "mistral-large-2411"
    client_text = Mistral(api_key=api_key)
    response = await client_text.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"Улучши запрос для нейросети Flux, которая генерирует изображения, нужен английский язык, вот запрос: {req}",
            },
        ],
    )
    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    response = await client.images.generate(
        model="flux",
        prompt=full_response,
        response_format="b64_json",
    )
    return response.data[0].b64_json


async def code_generation(req):
    api_key = os.getenv("AITOKEN")
    model = "codestral-2405"
    client = Mistral(api_key=api_key)
    response = await client.chat.stream_async(
        model=model,
        messages=req,
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
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "pixtral-large-2411",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image}",
                    },
                ],
            },
        ],
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Извините, не удалось получить ответ от AI"


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def search_with_mistral(query: str) -> str:
    api_key = os.getenv("AITOKEN")
    model = "mistral-large-2411"
    client = Mistral(api_key=api_key)
    response = await client.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Сформулируй наиболее эффективный и релевантный запрос для веб-поиска, чтобы ответить на сообщение пользователя: '{query}'. Верни только текст поискового запроса.",
            },
        ],
    )

    web_search_text = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            web_search_text += content

    searcher = duckduckgo_search.DDGS()
    search_data = searcher.text(
        web_search_text,
        safesearch="off",
        max_results=3,
        region="ru-ru",
    )
    web_data = []
    async with httpx.AsyncClient() as client_http:
        for result in search_data:
            try:
                response_http = await client_http.get(result["href"], timeout=10)
                response_http.raise_for_status()
                soup = BeautifulSoup(response_http.text, "html.parser")
                paragraphs = soup.find_all("p")
                page_text = " ".join([p.text for p in paragraphs])
                web_data.append(
                    f"Источник: {result['href']}\nСодержание: {page_text[:550]}...",
                )
            except Exception as e:
                logger.error(f"Ошибка при парсинге {result['href']}: {e}")
                web_data.append(f"Не удалось получить содержимое с {result['href']}")

    response = await client.chat.stream_async(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Используя только информацию, представленную в содержании следующих веб-страниц, ответь на вопрос пользователя. Синтезируй информацию из разных источников, чтобы дать полный и точный ответ. Избегай домыслов и не добавляй информацию, которой нет на предоставленных страницах. Вот содержание веб-страниц:\n\n{' '.join(web_data)}\n\nВопрос пользователя: {query}",
            },
            {
                "role": "user",
                "content": query
            },
        ],
    )
    full_response = ""
    async for chunk in response:
        content = chunk.data.choices[0].delta.content
        if content is not None:
            full_response += content

    return full_response if full_response else "Ошибка: пустой ответ от AI"
