from google import genai

from app.core import exceptions
from app.core.config import settings


client = genai.Client(api_key=settings.gemini_key)

async def suggest_tags(title: str, content: str):
    prompt = f"""
    Analyze this blog post and suggest up to 5 relevant tags.

    Title:
    {title}

    Content:
    {content}

    Return only the tag names separated by commas.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    if response is None or not response.text:
        raise exceptions.GeminiResponseError()

    return [tag.strip() for tag in response.text.split(",")]

