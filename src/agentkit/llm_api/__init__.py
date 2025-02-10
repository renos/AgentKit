token_counter = {"token_completion": {}, "token_prompt": {}, "api_calls": {}}


def get_token_counts():
    global token_counter
    return token_counter


def query_gpt_chat(model):
    from .GPT import GPT_chat

    global token_counter
    query_model = GPT_chat(model, token_counter)
    return query_model


def query_claude_chat(model):
    from .claude import Claude_chat

    global token_counter
    query_model = Claude_chat(model, token_counter)
    return query_model


def query_ollama_chat(model):
    from .ollama import Ollama_chat

    global token_counter
    # model = model.replace('ollama-','')
    query_model = Ollama_chat(model, token_counter)
    return query_model


def query_sambanova_chat(model):
    from .samba import Samba_chat

    global token_counter
    query_model = Samba_chat(model, token_counter)
    return query_model


def query_gemini_chat(model):
    from .gemini import Gemini_chat

    global token_counter
    query_model = Gemini_chat(model, token_counter)
    return query_model


def get_query(LLM_name):
    """Get the query model for the specified LLM_name.

    Currently supported LLMs:

    - GPT-4

    - GPT-3.5

    - Claude

    - Ollama

    Args:
        LLM_name (str): Name of the LLM model
        tokenmodel_path (str): Path to the token model

    Returns:
        LLM_API_FUNCTION: The query model for the specified LLM_name
    """
    print(
        "Warning: The built-in LLM API is only for testing, and will not be actively maintained. Please write your own API for production use."
    )
    if (
        LLM_name.lower().startswith("gpt-4")
        or LLM_name.lower().startswith("gpt-3.5")
        or LLM_name.lower().startswith("o1")
    ):
        return query_gpt_chat(model=LLM_name)
    elif LLM_name.lower().startswith("claude"):
        return query_claude_chat(model=LLM_name)
    elif LLM_name.lower().startswith("ollama-"):
        return query_ollama_chat(model=LLM_name)
    elif LLM_name.lower().startswith("sambanova-"):
        return query_sambanova_chat(model=LLM_name)
    elif LLM_name.lower().startswith("google-"):
        return query_gemini_chat(model=LLM_name)
    else:
        raise NotImplementedError("LLM {} not implemented".format(LLM_name))
