import os
from flask import current_app, g
from openai import OpenAI
from config import Config


def get_openai_client():
    if "openai_client" not in g:
        g.openai_client = OpenAI(api_key=Config.OPEN_API_KEY)
    return g.openai_client
