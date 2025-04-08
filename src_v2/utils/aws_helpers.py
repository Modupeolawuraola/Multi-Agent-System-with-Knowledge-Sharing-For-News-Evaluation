
import os
import boto3
from dotenv import load_dotenv

# Make sure to load environment variables
# env_path = os.path.join('..', '.env')
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
        client = session.client('bedrock-runtime')
        # Simple operation to test connection
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


def get_bedrock_client():
    """Get authenticated Bedrock client"""
    # Get AWS credentials
    credentials = get_aws_credentials()

    try:
        if credentials['aws_access_key_id'] and credentials['aws_secret_access_key']:
            session = boto3.Session(**credentials)
            client = session.client("bedrock-runtime")
        else:
            # If no credentials, use default credentials from environment
            client = boto3.client("bedrock-runtime", region_name=credentials['region_name'])

        return client
    except Exception as e:
        print(f"Error creating Bedrock client: {e}")
        raise


def get_bedrock_llm():
    """Get LLM client for direct interactions"""
    from langchain_aws import ChatBedrock

    # In the new architecture, we always use real AWS services
    print("Using real AWS Bedrock for direct KG interactions")

    try:
        client = get_bedrock_client()

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


def test_neo4j_connection():
    """Test Neo4j connection and create necessary constraints/indexes"""
    from langchain_neo4j import Neo4jGraph

    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )

        # Test simple query
        result = graph.query("RETURN 'Neo4j connection successful' as message")
        print(result[0]['message'])

        # Create constraint on Article nodes
        graph.query("""
        CREATE CONSTRAINT article_url_constraint IF NOT EXISTS
        FOR (a:Article) REQUIRE a.url IS UNIQUE
        """)

        # Create indexes for improved query performance
        graph.query("""
        CREATE INDEX article_title_idx IF NOT EXISTS
        FOR (a:Article) ON (a.title)
        """)

        return True
    except Exception as e:
        print(f"Neo4j connection error: {e}")
        return False