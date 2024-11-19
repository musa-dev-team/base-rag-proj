import base64
import json
import re
from time import sleep
import traceback
from typing import List
from bs4 import BeautifulSoup
import html2text
from requests import Response
from dotenv import load_dotenv
import logging

load_dotenv()

def rate_limit_function(
    func, retry_timer=2, max_retry_timer=60 * 5, error_message="rate"
):
    def wrapper(*args, **kwargs):
        nonlocal retry_timer
        nonlocal max_retry_timer
        nonlocal error_message

        while True:
            try:
                response = func(*args, **kwargs)
                if isinstance(response, Response):
                    response.raise_for_status()
                return response
            except Exception as e:
                if retry_timer > max_retry_timer:
                    logging.error(
                        f"Rate limit exceeded on function: {str(func.__name__)}"
                    )
                    raise e
                if (
                    error_message.lower() in str(e).lower()
                    or ("rate" in str(e).lower() and "limit" in str(e).lower())
                    or "too many requests" in str(e).lower()
                ):
                    logging.warning(
                        f"{str(func.__name__)} - Rate limited, retrying in {str(retry_timer)} seconds."
                    )
                    sleep(retry_timer)
                    retry_timer *= 2
                else:
                    logging.error(
                        f"Error in rate_limit_function: {str(e)}\n{traceback.format_exc()}"
                    )
                    raise e

    return wrapper

def file_to_image_data(file_content, mime_type):
    base64_encoded_data = base64.b64encode(file_content).decode("utf-8")
    return f"data:{mime_type};base64,{base64_encoded_data}"

def file_image_data_to_bytes(data_url):
    # Remove the "data:mime/type;base64," prefix
    header, encoded = data_url.split(",", 1)
    # Decode the base64 string
    bytes_data = base64.b64decode(encoded)
    return bytes_data

def html_to_markdown(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # Handle images specifically
    for img in soup.find_all("img"):
        alt_text = img.get("alt", "")
        src = img.get("src", "")
        # Replace the img tag with the Markdown equivalent
        img.replace_with(f"![{alt_text}]({src})")

    text_maker = html2text.HTML2Text()
    text_maker.body_width = 0
    text_maker.ignore_links = False
    markdown_content = text_maker.handle(str(soup))

    return markdown_content


def extract_file_url_markdown(text):
    pattern = r"!\[([^\]]*)\]\((https?:\/\/[^\s]+)\)"

    matches = re.findall(pattern, text)
    results = []

    for match in matches:
        filename, url = match
        file_extension = re.search(r"\.(\w+)$", filename)
        if file_extension:
            extension = file_extension.group(1)
        else:
            extension = "unknown"

        results.append({"url": url, "extension": extension})

    return results


def get_num_tokens(text, model="gpt-4o"):
    import tiktoken

    tokenizer = tiktoken.encoding_for_model(model)
    return len(tokenizer.encode(text))


def truncate_text(text, max_tokens, model="gpt-4o"):
    import tiktoken

    tokenizer = tiktoken.encoding_for_model(model)
    tokens = tokenizer.encode(text)
    return tokenizer.decode(tokens[:max_tokens])


def random_string():
    import random
    import string

    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

def cprint(text, color="green"):
    from rich import print as rprint

    if isinstance(text, dict):
        try:
            text = json.dumps(text, indent=4)
        except Exception as e:
            logging.warning(f"Failed to convert text to json: {e}")
            text = str(text)

    rprint(f"[{color}]{text}[/{color}]")

def extract_urls_from_output(output: str) -> List[str]:
    urls = []
    lines = output.strip().split('\n')
    
    pattern = re.compile(r'^\d+,\s*(\{.*\})$')
    
    for line in lines:
        match = pattern.match(line)
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)
                url = data.get("url")
                if url:
                    urls.append(url)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in line: {line}\nError: {e}")
    
    return urls
