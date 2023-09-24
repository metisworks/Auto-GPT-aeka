from autogpt.llm.base import ResponseMessageDict
from autogpt.llm.providers.openai import create_chat_completion
from autogpt.logs import logger

GPT_4_MODEL = "gpt-4"
GPT_3_MODEL = "gpt-3.5-turbo"
OPENAI_KEY = "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"


def execute_prompt_chat(messages, **kwargs):
    chat_completion_kwargs = {
        "model": GPT_3_MODEL,
        "temperature": 0,
        "api_key": OPENAI_KEY,
        "api_base": None,
        "organization": None
    }
    results = create_chat_completion(messages=messages,**chat_completion_kwargs)
    logger.debug(f"{results = }")
    if hasattr(results, "error"):
        logger.error(results.error)
        raise RuntimeError(results.error)
    first_message: ResponseMessageDict = results.choices[0].message
    content: str | None = first_message.get("content")
    content = content.strip('\\').strip('\"')
    return content