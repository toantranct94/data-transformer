import json
from functools import wraps
from typing import List

from groq import AsyncGroq, GroqError
from groq.types.chat.chat_completion import ChatCompletion
from loguru import logger

from app.configs import settings
from app.utils import text_util


def retry_on_failure(fallback_model: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GroqError as e:
                logger.warning(f"Error: {e}, retrying with model: {fallback_model}")
                kwargs["model"] = fallback_model
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error: {e}")
                raise e

        return wrapper

    return decorator


@retry_on_failure(settings.GROQ_AI_FALLBACK_MODEL)
async def async_chat_completion(
    messages: List,
    model: str = settings.GROQ_AI_DEFAULT_MODEL,
    force_json_output: bool = False,
    reasoning_format: str = "hidden",
    stream: bool = False,
):
    async_client = AsyncGroq()
    logger.info(f"Prompt to GroqAI: {json.dumps(messages)} \n Model: {model}")

    response_format = {"type": "json_object"} if force_json_output else None

    response = await async_client.chat.completions.create(
        model=model,
        messages=messages,
        reasoning_format=reasoning_format,
        response_format=response_format,
        stream=stream,
    )

    return process_response(response, force_json_output)


def process_response(response: ChatCompletion, force_json_output: bool):
    response = handle_response_from_groq_ai(response)
    if force_json_output:
        return text_util.try_parse_string(response, default={})
    return response


def handle_response_from_groq_ai(response: ChatCompletion, default: str = "[]"):
    choice = response.choices[0]
    finish_reason_handlers = {
        "function_call": lambda: choice.message.function_call.arguments,
        "stop": lambda: choice.message.content,
        "tool_calls": lambda: choice.message.tool_calls[0].function.arguments,
    }
    return finish_reason_handlers.get(choice.finish_reason, lambda: default)()
