import os
import boto3
from dotenv import load_dotenv

# Make sure to load environment variables
load_dotenv()


def diagnostic_check():
    """Run diagnostic checks for AWS credentials"""
    print("==== AWS CREDENTIAL DIAGNOSTIC ====")
    print(f"Working directory: {os.getcwd()}")
    print(f"AWS_ACCESS_KEY_ID: {'FOUND' if os.environ.get('AWS_ACCESS_KEY_ID') else 'MISSING'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'FOUND' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'MISSING'}")
    print(f"AWS_SESSION_TOKEN: {'FOUND' if os.environ.get('AWS_SESSION_TOKEN') else 'MISSING'}")
    print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'us-east-1')}")

    # Test Bedrock connection
    try:
        session = boto3.Session(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        client = session.client('bedrock')
        # Remove the maxResults parameter that's causing validation errors
        client.list_foundation_models()
        print("✅ Bedrock connection successful")
    except Exception as e:
        print(f"❌ Bedrock connection failed: {e}")
    print("==================================")


def get_aws_credentials():
    """Get AWS credentials from environment variables"""
    # Check for environment variables
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
    if not access_key:
        print("WARNING: AWS_ACCESS_KEY_ID not found in environment")

    # Get region with fallback
    region = os.environ.get('AWS_REGION', 'us-east-1')
    print(f"Using AWS region: {region}")

    return {
        'aws_access_key_id': access_key,
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
        'aws_session_token': os.environ.get('AWS_SESSION_TOKEN', ''),
        'region_name': region
    }


def get_bedrock_llm():
    """Get LLM client based on environment."""
    from langchain_aws import ChatBedrock

    if os.environ.get("USE_REAL_SERVICES", "False").lower() == "true":
        # Use real AWS - explicitly requested
        print("Using REAL AWS for LLM (explicitly requested)")

        # Get AWS credentials
        credentials = get_aws_credentials()

        # Create client
        try:
            if credentials['aws_access_key_id'] and credentials['aws_secret_access_key']:
                session = boto3.Session(**credentials)
                client = session.client("bedrock-runtime")
            else:
                # If no credentials, use default credentials from environment
                client = boto3.client("bedrock-runtime", region_name=credentials['region_name'])

            # Create and return LLM
            return ChatBedrock(
                client=client,
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                model_kwargs={
                    "max_tokens": 4096,
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            )
        except Exception as e:
            print(f"Error creating real Bedrock LLM: {e}")
            raise

    elif os.environ.get("TESTING", "False").lower() == "true":
        # Use mock for regular tests
        print("Using MOCK for LLM (testing mode)")
        from unittest.mock import MagicMock

        mock_llm = MagicMock()
        # Configure mock to return empty JSON responses
        mock_llm.invoke.return_value.content = "{}"
        return mock_llm

    else:
        # Default behavior - use real AWS (your original implementation)
        print("Using real AWS Bedrock (default)")

        # Get AWS credentials
        credentials = get_aws_credentials()

        # Create client
        try:
            if credentials['aws_access_key_id'] and credentials['aws_secret_access_key']:
                session = boto3.Session(**credentials)
                client = session.client("bedrock-runtime")
            else:
                # If no credentials, use default credentials from environment
                client = boto3.client("bedrock-runtime", region_name=credentials['region_name'])

            # Create and return LLM
            return ChatBedrock(
                client=client,
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                model_kwargs={
                    "max_tokens": 4096,
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            )
        except Exception as e:
            print(f"Error creating Bedrock LLM: {e}")
            raise
