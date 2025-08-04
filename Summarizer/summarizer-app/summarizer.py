import anthropic

# (Keep your API Key and client initialization the same)
CLAUDE_API_KEY = ""
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def handle_api_call(system_prompt, user_prompt, max_tokens=1024):
    # (handle_api_call function remains the same)
    if not client:
        return "Error: Anthropic API client is not initialized. Please check your API key."
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"


# --- MODIFIED: summarize_text function now accepts 'length' ---
def summarize_text(text_to_summarize: str, length: str = 'medium') -> str:
    """Calls the Claude API to summarize text to a specified length."""
    if not text_to_summarize.strip():
        return "Error: Input text cannot be empty."

    # Define different instructions based on the desired length
    length_instructions = {
        "short": "Provide a very brief, one-paragraph summary.",
        "medium": "Provide a detailed summary that is a few paragraphs long.",
        "long": "Provide a comprehensive and detailed summary, covering all key points thoroughly."
    }
    
    instruction = length_instructions.get(length, length_instructions['medium'])
    
    system_prompt = f"You are a world-class expert in summarizing text. Your goal is to provide a clear and concise summary of the provided content. {instruction}"
    user_prompt = f"Please summarize the following text:\n\n{text_to_summarize}"
    
    return handle_api_call(system_prompt, user_prompt)


def generate_essay(topic: str) -> str:
    # (generate_essay function remains the same)
    if not topic.strip():
        return "Error: Essay topic cannot be empty."
    system_prompt = "You are a helpful and knowledgeable writing assistant..."
    user_prompt = f"Please write an essay on the following topic: {topic}"
    return handle_api_call(system_prompt, user_prompt)
