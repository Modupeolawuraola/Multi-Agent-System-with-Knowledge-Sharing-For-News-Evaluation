import os
import sys
import boto3
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', '.env')
load_dotenv(dotenv_path)


def debug_aws_credentials():
    """Debug AWS credential issues"""
    print("\n===== DETAILED AWS CREDENTIAL CHECK =====")

    # Check environment variables
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'Not set')
    session_token = os.environ.get('AWS_SESSION_TOKEN', '')
    region = os.environ.get('AWS_REGION', 'Not set')

    print(f"Access Key ID: {access_key[:4]}... (length: {len(access_key)})")
    print(f"Secret Key: {secret_key[:4]}... (length: {len(secret_key)})")
    print(f"Session Token: (length: {len(session_token)})")
    print(f"Region: {region}")

    # Try S3 access
    print("\nTesting S3 access...")
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print(f"✅ S3 connection successful - found {len(response['Buckets'])} buckets")
    except Exception as e:
        print(f"❌ S3 connection failed: {str(e)}")

    # Try regular Bedrock service
    print("\nTesting Bedrock service...")
    try:
        bedrock = boto3.client('bedrock')
        response = bedrock.list_foundation_models()
        print(f"✅ Bedrock connection successful")
        print(f"Available models: {len(response.get('modelSummaries', []))}")
    except Exception as e:
        print(f"❌ Bedrock connection failed: {str(e)}")

    # Try Bedrock runtime
    print("\nTesting Bedrock runtime...")
    try:
        runtime = boto3.client('bedrock-runtime')
        print(f"✅ Bedrock runtime client created successfully")
    except Exception as e:
        print(f"❌ Bedrock runtime connection failed: {str(e)}")

    print("\n========================================")


if __name__ == "__main__":
    debug_aws_credentials()
