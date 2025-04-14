from dotenv import load_dotenv
import boto3
import os
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src_v3', '.env')

def test_aws_credentials():
    """Test AWS credentials are properly loaded and can access Bedrock"""
    try:
        # Explicitly point to .env file in src directory
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', '.env')
        load_dotenv(dotenv_path)

        # Check if credentials exist
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        aws_region = os.getenv('AWS_REGION')

        if not all([aws_access_key, aws_secret_key, aws_region, aws_session_token]):
            print("❌ Missing AWS credentials in .env file")
            missing = []
            if not aws_access_key: missing.append("AWS_ACCESS_KEY_ID")
            if not aws_secret_key: missing.append("AWS_SECRET_ACCESS_KEY")
            if not aws_session_token: missing.append("AWS_SESSION_TOKEN")
            if not aws_region: missing.append("AWS_REGION")
            print(f"Missing credentials: {', '.join(missing)}")
            return False

        # Create regular bedrock client for model listing
        bedrock = boto3.client(
            'bedrock',  # Use 'bedrock' instead of 'bedrock-runtime'
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
            region_name=aws_region
        )

        # List available models
        response = bedrock.list_foundation_models()

        # Create runtime client for actual inference
        runtime = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
            region_name=aws_region
        )

        print("✅ AWS credentials verified successfully!")
        print(f"Region: {aws_region}")
        print(f"Access Key: {aws_access_key[:8]}...")
        print("Available models:")
        for model in response['modelSummaries']:
            print(f"- {model['modelId']}")
        return True

    except Exception as e:
        print(f"❌ Error testing AWS credentials: {e}")
        return False


if __name__ == "__main__":
    test_aws_credentials()