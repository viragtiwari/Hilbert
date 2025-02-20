# Importing necessary types and functions
from typing import List, Optional
from model import chat

# Initialize the arrays to store chat history and context
chat_his: List[str] = []
context: List[dict] = []

def append_chat_history(prompt: str) -> None:
    """
    Append a prompt to the chat history array
    
    Args:
        prompt (str): The prompt to append
    
    Raises:
        TypeError: If the prompt is not a string
    """
    # Check if the prompt is a string
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string")
    # Append the prompt to the chat history
    chat_his.append(prompt)

def summarize(context_list: List[dict]) -> str:
    """
    Use LLM to summarize the given context list into a single string
    
    Args:
        context_list (List[dict]): List of context dictionaries to summarize
        
    Returns:
        str: Summarized context
    """
    # Debug: Print chat history
    print("\n=== Debug: Chat History ===")
    print(f"Number of context items: {len(context_list)}")
    for idx, message in enumerate(context_list):
        print(f"Message {idx + 1}:")
        print(f"Role: {message['role']}")
        print(f"Content: {message['content']}\n")

    # Prepare the conversation for the model
    conversation = [
        {
            "role": "system",
            "content": """*Briefly* summarize this partial conversation about programming.
                        Include less detail about older parts and more detail about the most recent messages.
                        Start a new paragraph every time the topic changes!

                        This is only part of a longer conversation so *DO NOT* conclude the summary with language like "Finally, ...". Because the conversation continues after the summary.
                        The summary *MUST* include the function names, libraries, packages that are being discussed.
                        The summary *MUST* include the filenames that are being referenced by the assistant inside the ```...``` fenced code blocks!
                        The summaries *MUST NOT* include ```...``` fenced code blocks!

                        Phrase the summary with the USER in first person, telling the ASSISTANT about the conversation.
                        Write *as* the user.
                        The user should refer to the assistant as *you*.
                        Start the summary with "I asked you...".
                    """
        },
        {
            "role": "user",
            "content": "\n".join([f"{message['role']}: {message['content']}" for message in context_list])
        }
    ]
    
    # Debug: Print model payload
    print("\n=== Debug: Model Payload ===")
    print("System prompt:", conversation[0]['content'])
    print("\nFormatted context for model:", conversation[1]['content'])
    
    try:
        # Call the model using the chat function from model.py
        summary = chat("You are a summarizer",conversation, "llama-3.1-8b-instant")
        print(f"\n=== Debug: Model Response {summary} ===")
        return summary
    except Exception as e:
        # If summarization fails, fall back to simple concatenation
        print(f"Warning: Summarization failed - {str(e)}")
        return "\n".join([message['content'] for message in context_list])

def append_context(role: str, content: str, summarize_bool: Optional[bool]) -> None:
    """
    Append a message to the context array with special handling when length reaches 5
    
    Args:
        role (str): The role of the message (e.g., "user", "assistant", "system")
        content (str): The content of the message
        
    Raises:
        TypeError: If role or content is not a string
        Exception: If summarization fails
    """
    # Check if role and content are strings
    if not isinstance(role, str) or not isinstance(content, str):
        raise TypeError("Role and content must be strings")
    
    global context
    
    # Create message dictionary
    message = {
        "role": role,
        "content": content
    }
    
    try:
        # If boolean is true, summarize and reset
        if summarize_bool == True:
            # Summarize existing context
            summarized = summarize(context)
            # Reset context with summarized content at index 0 and new message at index 1
            context = [
                {"role": "user", "content": f"Above is the summarized context: {summarized}"},
                {"role": "assistant", "content": "Understood I will continue the conversation."},
                message
            ]
        else:
            # If boolean is false, simply append the new message
            context.append(message)
    except Exception as e:
        raise Exception(f"Error in context management: {str(e)}")

def get_chat_history() -> List[str]:
    """Get the current chat history"""
    return chat_his

def get_context() -> List[dict]:
    """Get the current context"""
    return context

# Test cases
def run_tests() -> None:
    """Run test cases for the context management functions"""
    try:
        # Test chat history with realistic conversation
        append_chat_history("Can you help me create a web scraper using Python?")
        assert len(get_chat_history()) == 1
        
        # Test context management with a realistic conversation
        test_conversation = [
            ("user", "I need help creating a web scraper using Python. Which libraries should I use?"),
            ("assistant", "I recommend using BeautifulSoup4 and requests libraries for web scraping. They're powerful and easy to use. Would you like me to show you how to set them up?"),
            ("user", "Yes, please show me how to scrape a simple webpage."),
            ("assistant", "I'll help you create a basic scraper. First, let's install the required packages and write a script to scrape a webpage."),
            ("user", "Can you also add error handling for failed requests?"),
            ("assistant", "I'll add try-except blocks to handle connection errors and invalid URLs in the scraper code.")
        ]
        
        # Add conversation to context
        for role, content in test_conversation:
            append_context(role, content)
        
        # Get the context and verify summarization
        context = get_context()
        print("\n=== Test Context After Summarization ===")
        print(f"Final context length: {len(context)}")
        print("Context contents:")
        for item in context:
            print(f"Role: {item['role']}")
            print(f"Content: {item['content']}\n")
        
        # Test error handling
        try:
            append_context(123, "Context")  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass
            
        print("All tests passed!")
        
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in tests: {str(e)}")

"""
# Run tests if this script is executed directly
if __name__ == "__main__":
    run_tests()

"""