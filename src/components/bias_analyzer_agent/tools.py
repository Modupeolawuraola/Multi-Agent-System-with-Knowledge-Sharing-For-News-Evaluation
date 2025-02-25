
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import BedrockChat
from .b_prompts import (
    Bias_detection_prompt,
    Deep_analysis_prompt,
    Verify_prompt
)
from dotenv import load_dotenv
import boto3
import os

load_dotenv()


def create_bedrock_client():
    """Create bedrock authenticated Bedrock client"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        bedrock_client= session.client(service_name='bedrock-runtime',
                                       region_name=os.getenv('AWS_REGION', 'us-east-1')
                                       )
        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        raise

def create_llm():
    """Create Bedrock LLm Instance"""
    try:
        client = create_bedrock_client()
        #initialize anthropic calude model through bedrock

        llm= BedrockChat(
            client= client,
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens":4096,
                "temperature":0.2,
                "top_p":0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise




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