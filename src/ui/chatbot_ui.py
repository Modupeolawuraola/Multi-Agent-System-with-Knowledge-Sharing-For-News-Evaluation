import os
import streamlit as st
from dotenv import load_dotenv
import sys
from neo4j import GraphDatabase
import json
from datetime import datetime
import re
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.components.retriever_Agent.retriever_agent import RetrieverAgent

# Load environment variables
load_dotenv()

# Initialize LLM using Mistral through Ollama
llm = Ollama(
    model="mistral",
    temperature=0.7,
    base_url="http://localhost:11434"  # Default Ollama URL
)

# Define prompt templates
SYSTEM_PROMPT = """You are an advanced news analysis and evaluation assistant. Your role is to:
1. Evaluate the credibility of news articles
2. Identify potential biases and misleading information
3. Analyze sources and factual consistency
4. Provide balanced perspectives on news topics
5. Help users understand the reliability of news content

Always maintain a professional and objective tone. When analyzing news:
- Examine sources for credibility and reliability
- Evaluate language tone for neutrality
- Check factual consistency throughout the article
- Identify any potential biases or partisan leanings
- Look for exaggerations or sensationalized content"""

CREDIBILITY_TEMPLATE = """Evaluate the credibility of this news article:

Article Content: {context}
User Query: {query}

Consider and analyze:
1. Sources: Are they credible and reliable?
2. Tone: Is it neutral or emotionally charged?
3. Factual consistency: Are claims accurate and consistent?
4. Bias: Is there favoritism toward particular viewpoints?

Provide a detailed analysis addressing each aspect."""

BIAS_ANALYSIS_TEMPLATE = """Analyze this news article for potential biases and misleading information:

Article Content: {context}
User Query: {query}

Examine and report on:
1. Biases: Identify language choices or framing showing partiality
2. Misleading information: Find claims taken out of context
3. Exaggerations: Look for sensationalized statements
4. Overall reliability: Rate and explain the article's reliability

Provide specific examples and a comprehensive analysis."""

# Create prompt templates
credibility_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", CREDIBILITY_TEMPLATE)
])

bias_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", BIAS_ANALYSIS_TEMPLATE)
])

# Create chains
credibility_chain = credibility_prompt | llm | StrOutputParser()
bias_chain = bias_prompt | llm | StrOutputParser()

def get_llm_response(query: str, context: str = "", analysis_type: str = "general") -> str:
    """Get response from LLM using the provided query and context"""
    try:
        if "credibility" in query.lower() or "evaluate" in query.lower():
            response = credibility_chain.invoke({
                "query": query,
                "context": context
            })
        elif "bias" in query.lower() or "misleading" in query.lower():
            response = bias_chain.invoke({
                "query": query,
                "context": context
            })
        else:
            # Use a general response template for other queries
            general_prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Based on this context: {context}\nAnswer this query: {query}")
            ])
            general_chain = general_prompt | llm | StrOutputParser()
            response = general_chain.invoke({
                "query": query,
                "context": context
            })
        return response
    except Exception as e:
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

def test_neo4j_connection():
    """Test the connection to Neo4j database"""
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    
    if not all([uri, username, password]):
        return False, "Missing Neo4j credentials in environment variables"
    
    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            driver.verify_connectivity()
            return True, "Successfully connected to Neo4j database"
    except Exception as e:
        return False, f"Failed to connect to Neo4j: {str(e)}"

# Initialize session state for conversation context
if 'conversation_context' not in st.session_state:
    st.session_state.conversation_context = {
        'greeted': False,
        'user_name': None,
        'last_topic': None,
        'topics_discussed': set()
    }

def get_greeting():
    """Get appropriate greeting based on time of day"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def process_user_input(prompt: str):
    """Process user input to understand intent and extract key information"""
    prompt_lower = prompt.lower()
    
    # Get articles from knowledge graph for context
    articles = query_knowledge_graph(prompt)
    
    # Create context from articles
    context = ""
    if isinstance(articles, str) and not articles.startswith("Error"):
        context = articles
    
    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in prompt_lower for greeting in greetings):
        if not st.session_state.conversation_context['greeted']:
            st.session_state.conversation_context['greeted'] = True
            return {
                'type': 'greeting',
                'response': get_llm_response(
                    prompt,
                    "This is the first interaction with the user. Provide a friendly greeting and explain your capabilities."
                )
            }
        else:
            return {
                'type': 'greeting',
                'response': get_llm_response(
                    prompt,
                    "This is a follow-up greeting. Keep it brief and ask about their news interests."
                )
            }
    
    # Check for personal questions about the bot
    if 'who are you' in prompt_lower or 'what can you do' in prompt_lower:
        return {
            'type': 'introduction',
            'response': get_llm_response(
                prompt,
                "The user is asking about your capabilities. Explain your role as a news analysis assistant."
            )
        }
    
    # Check for thank you messages
    if 'thank' in prompt_lower or 'thanks' in prompt_lower:
        return {
            'type': 'gratitude',
            'response': get_llm_response(
                prompt,
                "The user is expressing gratitude. Provide a polite response and encourage further questions."
            )
        }
    
    # Check for goodbyes
    if 'bye' in prompt_lower or 'goodbye' in prompt_lower:
        return {
            'type': 'farewell',
            'response': get_llm_response(
                prompt,
                "The user is saying goodbye. Provide a friendly farewell and invite them to return."
            )
        }
    
    # Process news-related queries with LLM
    return {
        'type': 'query',
        'response': get_llm_response(prompt, context)
    }

def extract_keywords(text):
    """Extract important keywords from the query"""
    # Remove common words and keep important ones
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 
                   'show', 'me', 'find', 'search', 'get', 'about', 'of', 'with', 'by', 'from', 'up', 'down', 'what',
                   'articles', 'news', 'information', 'tell', 'give'}
    
    # Split into words and remove punctuation
    words = re.findall(r'\w+', text.lower())
    # Filter out common words and short words (length < 2)
    keywords = [word for word in words if word not in common_words and len(word) > 2]
    return keywords if keywords else None

def query_knowledge_graph(prompt: str):
    """Query the knowledge graph for relevant articles"""
    try:
        # Extract keywords for search
        keywords = extract_keywords(prompt)
        
        # Initialize graph state
        initial_state = {
            "knowledge_graph": {"articles": []},
            "articles": [],
            "current_status": "ready",
            "error": None
        }

        # Connect to Neo4j and get current graph state
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')
        
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                # Construct query to find relevant articles with improved search
                query = """
                MATCH (a:Article)
                WHERE $keywords IS NULL OR 
                      ANY(keyword IN $keywords WHERE 
                          toLower(a.title) CONTAINS toLower(keyword) OR
                          toLower(COALESCE(a.text, '')) CONTAINS toLower(keyword) OR
                          toLower(COALESCE(a.description, '')) CONTAINS toLower(keyword) OR
                          toLower(COALESCE(a.full_text, '')) CONTAINS toLower(keyword))
                OPTIONAL MATCH (a)-[:HAS_ENTITY]->(e)
                WITH a, COLLECT(DISTINCT CASE WHEN e IS NOT NULL THEN e END) as entities
                RETURN a, entities
                ORDER BY a.publishedAt DESC
                LIMIT 10
                """
                
                result = session.run(
                    query,
                    keywords=keywords
                )
                
                articles = []
                for record in result:
                    article = record["a"]
                    entities = record["entities"]
                    
                    # Get the actual content field based on what's available
                    content = None
                    for field in ["text", "full_text", "description"]:
                        if article.get(field):
                            content = article.get(field)
                            break
                    
                    # If no content is found, use title
                    if not content:
                        content = article.get("title", "No content available")
                    
                    # Highlight keywords in content if they exist
                    if keywords and content:
                        highlighted_content = content
                        for keyword in keywords:
                            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                            highlighted_content = pattern.sub(f"**{keyword}**", highlighted_content)
                        content = highlighted_content
                    
                    article_data = {
                        "title": article.get("title", "No title"),
                        "content": content,
                        "source": article.get("source_name", article.get("source", "Unknown source")),
                        "date": article.get("publishedAt", "No date"),
                        "entities": [e.get("name") for e in entities if e is not None],
                        "url": article.get("url", "")
                    }
                    
                    # Only add articles that match the search criteria
                    if keywords:
                        content_lower = content.lower()
                        title_lower = article_data["title"].lower()
                        if any(keyword in content_lower or keyword in title_lower for keyword in keywords):
                            articles.append(article_data)
                    else:
                        articles.append(article_data)

                if not articles:
                    suggested_terms = ""
                    if keywords:
                        suggested_terms = f"\n\nTry using different keywords. Your search used: {', '.join(keywords)}"
                    return f"No articles found matching your search.{suggested_terms}\n\nTips:\n- Use specific keywords\n- Try broader terms\n- Check for spelling"

                initial_state["knowledge_graph"]["articles"] = articles
                initial_state["articles"] = articles

        # Format response
        response = []
        for article in articles:
            article_info = [
                f"📰 **{article['title']}**",
                f"📅 Date: {article['date']}",
                f"📍 Source: {article['source']}",
                f"\n📝 Content: {article['content'][:500]}...",  # Show more content
            ]
            
            if article['entities']:
                article_info.append(f"\n🔑 Key Entities: {', '.join(article['entities'])}")
            
            if article.get('url'):
                article_info.append(f"\n🔗 [Read full article]({article['url']})")
            
            response.append("\n".join(article_info))
            response.append("\n---\n")
        
        # Add search summary
        if keywords:
            response.insert(0, f"🔍 Found {len(articles)} articles matching your search terms: {', '.join(keywords)}\n\n---\n")
        
        return "\n".join(response)
        
    except Exception as e:
        return f"Error querying knowledge graph: {str(e)}"

# Set page config
st.set_page_config(
    page_title="News Knowledge Graph Chatbot",
    page_icon="📰",
    layout="wide"
)

# Header
st.title("📰 News Knowledge Graph Chatbot")
st.markdown("""
I'm your intelligent news assistant. I can help you understand news articles, find connections between events, 
and track developments in topics you're interested in.
""")

# Sidebar with connection status
with st.sidebar:
    # Add connection status
    st.subheader("Connection Status")
    is_connected, status_msg = test_neo4j_connection()
    if is_connected:
        st.success("✅ Connected to Knowledge Graph")
    else:
        st.error(f"❌ Not Connected: {status_msg}")
    
    st.markdown("---")

# Initialize message history if not exists
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial greeting
if not st.session_state.messages:
    with st.chat_message("assistant"):
        greeting = f"{get_greeting()}! I'm your news assistant. How can I help you today?"
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})

# User input
if user_input := st.chat_input("Ask me about the news:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process the input and get response
    with st.chat_message("assistant"):
        processed = process_user_input(user_input)
        
        if processed['type'] == 'query':
            with st.spinner("Searching news articles..."):
                response = processed['response']
        else:
            response = processed['response']
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Add a clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.conversation_context = {
        'greeted': False,
        'user_name': None,
        'last_topic': None,
        'topics_discussed': set()
    }
    st.rerun()

# Help section
with st.sidebar.expander("ℹ️ Help"):
    st.markdown("""
    ### How to use:
    Just type your query and press Enter! You can:
    - Search for specific topics
    - Ask about recent news
    - Find articles by keywords
    
    ### Example queries:
    - "Show me articles about technology"
    - "Find news about climate change"
    - "What are the latest political updates?"
    
    ### Coming Soon:
    - Bias Detection: Analyze articles for potential bias
    - Fact Checking: Verify claims in articles
    - Entity Network: Visualize connections between people and organizations
    """) 