from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from src_v2.utils.aws_helpers import get_aws_credentials, diagnostic_check
from .b_prompts import (
    Bias_detection_prompt,
    Deep_analysis_prompt,
    Verify_prompt,
    BiasAnalysisSimplifiedPrompt
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
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", #anthropic.claude-3-sonnet-20240229-v1:0
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
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        )

        chain = (
                RunnablePassthrough() |
                BiasAnalysisSimplifiedPrompt |
                llm
        )

        return chain
        # Create a chain that's designed for direct KG interaction
        # chain = (
        #         RunnablePassthrough()
        #         | {"article_text": lambda x: format_article(x)["article_text"],
        #            "similar_articles_context": lambda x: x.get("similar_articles_context", "")}
        #         | Bias_detection_prompt
        #         | llm
        #         | (lambda ai_msg: {"detection_result": ai_msg.content})  # <-- Fix here
        #         | Deep_analysis_prompt
        #         | llm
        #         | (lambda ai_msg: {"analysis_result": ai_msg.content})  # <-- Fix here
        #         | Verify_prompt
        #         | llm
        #         | (lambda ai_msg: {"final_result": ai_msg.content})
        # )

        return chain
    except Exception as e:
        print(f"Error creating bias analysis chain: {e}")
        raise

def format_article(article: dict) -> dict:
    """Formats article for analysis"""
    title = article.get('title') or article.get('headline') or 'Untitled'
    content = article.get('full_content') or article.get('content') or ''
    source = article.get('source') or article.get('source_name') or 'Unknown Source'
    date = article.get('date') or article.get('publishedAt') or 'No date provided'

    formatted_text = f"""
    Title: {title}
    Content: {content}
    Source: {source}
    Date: {date}
    """
    # return dictionary with the formatted text
    return {
        "article_text": formatted_text,
        "original_text": article
    }

def format_similar_articles(similar_context: list) -> str:
    if not similar_context:
        return "No similar articles found in the knowledge graph."
    return "\n".join(
        f"- {a['title']} | Bias: {a['bias']} | Similarity Score: {round(a['similarity'], 2)}"
        for a in similar_context
    )