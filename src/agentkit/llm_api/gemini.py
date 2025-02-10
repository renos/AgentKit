try:
    import openai
except ImportError:
    raise ImportError("Please install openai to use built-in LLM API.")
from openai import OpenAI
import time
import os
from .utils import match_model
from .base import BaseModel


def initialize_client():

    if os.environ.get("GEMINI_API_KEY"):
        return OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    openai_key_path = os.path.join(os.path.expanduser("~"), ".openai", "googleai.key")
    print(openai_key_path)
    if os.path.exists(openai_key_path):
        with open(openai_key_path, "r") as file:
            key_content = file.read()[:-1]
            return OpenAI(
                api_key=key_content,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        raise FileNotFoundError(
            """
            Please create a file at ~/.openai/googleai.key with your Gemini API key. 
            The first line should be your API key
            """
        )


client_and_deployment = initialize_client()
client = (
    client_and_deployment[0]
    if isinstance(client_and_deployment, tuple)
    else client_and_deployment
)
deployment_name = (
    client_and_deployment[1] if isinstance(client_and_deployment, tuple) else None
)


class Gemini_chat(BaseModel):

    def __init__(self, model_name, global_counter=None):
        model_max, enc_fn = match_model(model_name)
        model_name = model_name.replace("google-", "")
        self.enc_fn = enc_fn
        self.model_max = model_max
        super().__init__(model_name, global_counter, "chat")

    def encode(self, txt):
        return self.enc_fn.encode(txt)

    def decode(self, txt):
        return self.enc_fn.decode(txt)

    def query_chat(self, messages, shrink_idx, max_gen=512, temp=0.0):
        model_max = self.model_max
        # messages = self.shrink_msg(messages, shrink_idx, model_max - max_gen)
        while True:
            try:
                completion = client.chat.completions.create(
                    model=deployment_name if deployment_name else self.name,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_gen,
                )

                return completion.choices[0].message.content, {
                    "prompt": completion.usage.prompt_tokens,
                    "completion": completion.usage.completion_tokens,
                    "total": completion.usage.total_tokens,
                }
            except Exception as e:
                if self.debug:
                    raise e
                elif (
                    isinstance(e, openai.RateLimitError)
                    or isinstance(e, openai.APIStatusError)
                    or isinstance(e, openai.APITimeoutError)
                    or isinstance(e, openai.APIConnectionError)
                    or isinstance(e, openai.InternalServerError)
                ):
                    time.sleep(30)
                    print(e)
                elif "However, your messages resulted in" in str(e):
                    print("error:", e, str(e))
                    e = str(e)
                    index = e.find("your messages resulted in ")
                    import re

                    val = int(
                        re.findall(
                            r"\d+", e[index + len("your messages resulted in ") :]
                        )[0]
                    )
                    index2 = e.find("maximum context length is ")
                    model_max = int(
                        re.findall(
                            r"\d+", e[index2 + len("maximum context length is ") :]
                        )[0]
                    )
                    # messages = self.shrink_msg_by(messages, shrink_idx, val - model_max)
                else:
                    print("error:", e)
                    print("retrying in 5 seconds")
                    time.sleep(5)
