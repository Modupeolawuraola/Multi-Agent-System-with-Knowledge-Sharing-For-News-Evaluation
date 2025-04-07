from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from src.utils.aws_helpers import get_aws_credentials, diagnostic_check
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
    """Create authenticated Bedrock client"""
    try:
        # Get credentials using our helper function
        credentials = get_aws_credentials()

        # Print debug info without revealing secrets
        if credentials['aws_access_key_id']:
            print(
                f"Using access key ID: {credentials['aws_access_key_id'][:4]}...{credentials['aws_access_key_id'][-4:]}")
        else:
            print("WARNING: AWS_ACCESS_KEY_ID not found in environment")

        print(f"Using AWS region: {credentials['region_name']}")

        # Create session
        session = boto3.Session(**credentials)

        # Create client
        bedrock_client = session.client(service_name='bedrock-runtime')

        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        print(f"Current working directory: {os.getcwd()}")
        raise


def create_llm():
    """Create Bedrock LLM Instance"""
    try:
        # Always use real AWS Bedrock - no mocks
        print("Using real AWS Bedrock")
        client = create_bedrock_client()
        llm = ChatBedrock(
            client=client,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise  # raise error if AWS fails


def create_bias_analysis_chain():
    """Create the bias analysis chain"""
    try:
        # Always use real AWS Bedrock LLM - no mocks
        client = create_bedrock_client()
        llm = ChatBedrock(
            client=client,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        )

        # Create a chain that's designed for direct KG interaction
        chain = (
                RunnablePassthrough() |
                {"article_text": lambda x: format_article(x)["article_text"]} |
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

def format_article(article: dict) -> dict:
    """Formats article for analysis"""
    formatted_text = f"""
    Title: {article['title']}
    Content: {article['content']}
    Source: {article['source']}
    Date: {article.get('date', 'No date provided')}
    """
    # return dictionary with the formatted text
    return {
        "article_text": formatted_text,
        "original_text": article
    }
