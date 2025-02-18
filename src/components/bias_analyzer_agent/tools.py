
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .b_prompts import (
    Bias_detection_prompt,
    Deep_analysis_prompt,
    Verify_prompt
)
from dotenv import load_dotenv
import os

load_dotenv()


def create_llm():
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API key loaded: {api_key[:8]}...")
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-4",
        temperature=0.2
    )


def create_bias_analysis_chain():
    """Create the bias analysis chain"""
    try:
        llm = create_llm()

        # Create a simple chain using RunnablePassthrough
        chain = (
                RunnablePassthrough() |
                {"text": lambda x: format_article(x)} |
                Bias_detection_prompt |
                llm |
                Deep_analysis_prompt |
                llm |
                Verify_prompt |
                llm
        )

        return chain
    except Exception as e:
        print(f"Error creating bias analysis chain: {e}")
        raise


def format_article(article: dict) -> str:
    """Formats article for analysis"""
    return f"""
    Title: {article['title']}
    Content: {article['content']}
    Source: {article['source']}
    Date: {article.get('date', 'No date provided')}
    """