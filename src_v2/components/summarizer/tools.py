import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src_v2.utils.aws_helpers import get_bedrock_client

def format_article(article: dict) -> dict:
    """Formats article for analysis"""
    return {
        "title": article['title'],
        "content": article['content'],
        "source": article['source'],
        "published_at": article.get('published_at', 'No date provided'),
        "related_articles": article.get('related_articles', [])
    }

def create_summarization_chain():
    """Create the summarization chain using Claude 3.5 Sonnet"""
    try:
        client = get_bedrock_client()
        
        class SummarizationChain:
            def __init__(self, client):
                self.client = client
            
            def invoke(self, article):
                # Format article content for the prompt
                article_text = f"""
                Title: {article['title']}
                Content: {article['content']}
                Source: {article['source']}
                Date: {article['published_at']}
                """
                
                # Get content summary
                content_request = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Please provide a comprehensive summary of this article:\n\n{article_text}"
                        }
                    ]
                }
                
                content_response = self.client.invoke_model(
                    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                    body=json.dumps(content_request)
                )
                content_summary = json.loads(content_response['body'].read())['content'][0]['text']
                
                # Get relationship analysis
                relationship_request = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"""Analyze the relationships and connections in this article. 
                            Focus on:
                            1. People mentioned and their roles
                            2. Organizations involved
                            3. Events described
                            4. Policies or issues discussed
                            5. How these entities are connected

                            Article content:
                            {article_text}"""
                        }
                    ]
                }
                
                relationship_response = self.client.invoke_model(
                    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                    body=json.dumps(relationship_request)
                )
                relationship_analysis = json.loads(relationship_response['body'].read())['content'][0]['text']
                
                return {
                    "content_summary": content_summary,
                    "relationship_analysis": relationship_analysis
                }
        
        return SummarizationChain(client)
        
    except Exception as e:
        print(f"Error creating summarization chain: {e}")
        raise 