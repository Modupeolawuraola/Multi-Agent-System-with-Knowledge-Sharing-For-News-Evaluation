
import os
import streamlit as st
from dotenv import load_dotenv
import sys
import json
from datetime import datetime
import re
import logging

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import from new architecture
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph
from src_v2.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v2.components.fact_checker.fact_checker_Agent import fact_checker_agent
from src_v2.memory.schema import GraphState
from src_v2.utils.aws_helpers import get_bedrock_llm, test_neo4j_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Initialize the knowledge graph
try:
    kg = KnowledgeGraph()
    llm = get_bedrock_llm()
    logging.info("Knowledge Graph and LLM initialized successfully")
except Exception as e:
    kg = None
    llm = None
    logging.error(f"Error initializing KG or LLM: {e}")

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


def process_bias_query(query):
    """Process a query related to bias detection"""
    try:
        if not kg or not llm:
            return "Sorry, I can't analyze bias right now because the Knowledge Graph or LLM is not available."

        # Create an initial state with the bias query
        state = GraphState(bias_query=query)

        # Process with bias analyzer agent
        result_state = bias_analyzer_agent(state, kg)

        if result_state.bias_analysis_result:
            return f"""
### Bias Analysis Results

**Overall Assessment**: {result_state.bias_analysis_result.get('overall_assessment', 'Not available')}

**Confidence Score**: {result_state.bias_analysis_result.get('confidence_score', '0')}%

**Key Findings**:
{', '.join(result_state.bias_analysis_result.get('findings', ['No specific findings']))}

**Recommendations**:
{', '.join(result_state.bias_analysis_result.get('recommendations', ['No specific recommendations']))}
            """
        else:
            return "I couldn't find any relevant bias information about your query. Try being more specific or searching for a different topic."

    except Exception as e:
        logging.error(f"Error in bias analysis: {e}")
        return f"I encountered an error while analyzing bias: {str(e)}"


def process_fact_check_query(query):
    """Process a query related to fact checking"""
    try:
        if not kg or not llm:
            return "Sorry, I can't fact-check right now because the Knowledge Graph or LLM is not available."

        # Create an initial state with the news query
        state = GraphState(news_query=query)

        # Process with fact checker agent
        result_state = fact_checker_agent(state, kg)

        if result_state.fact_check_result:
            claims = result_state.fact_check_result.get('verified_claims', [])
            report = result_state.fact_check_result.get('report', {})

            claims_text = ""
            if claims:
                for i, claim in enumerate(claims, 1):
                    verdict = claim.get('verification', {}).get('verdict', 'unknown')
                    confidence = claim.get('verification', {}).get('confidence', 0)
                    claims_text += f"**Claim {i}**: {claim.get('claim', 'Unknown claim')}\n"
                    claims_text += f"- Verdict: {verdict.capitalize()}\n"
                    claims_text += f"- Confidence: {int(confidence * 100)}%\n\n"

            return f"""
### Fact Check Results

**Overall Verdict**: {report.get('overall_verdict', 'Not available').capitalize()}

**Accuracy Rating**: {int(report.get('overall_accuracy', 0) * 100)}%

**Verified Claims**:
{claims_text if claims_text else "No specific claims were verified."}

**Key Issues**: {', '.join(report.get('key_issues', ['None identified']))}

**Recommendations**: {report.get('recommendations', 'No specific recommendations')}
            """
        else:
            return "I couldn't find any fact-check information about your query. Try being more specific or asking about a different topic."

    except Exception as e:
        logging.error(f"Error in fact checking: {e}")
        return f"I encountered an error while fact checking: {str(e)}"


def query_knowledge_graph(query):
    """Query the knowledge graph for relevant articles"""
    try:
        if not kg:
            return "Sorry, the Knowledge Graph is not available right now."

        # Extract keywords for search
        keywords = extract_keywords(query)
        if not keywords:
            return "I couldn't identify specific keywords in your query. Please try using more specific terms."

        # Get related articles from KG
        search_query = ' '.join(keywords)
        articles = kg.retrieve_related_articles(search_query, limit=5)

        if not articles:
            return f"No articles found matching your keywords: {', '.join(keywords)}. Try different search terms."

        # Format the results
        response = []
        response.append(f"🔍 Found {len(articles)} articles matching your search terms: {', '.join(keywords)}\n\n---\n")

        for article in articles:
            title = article.get('title', article.get('a.title', 'No title'))
            source = article.get('source_name', article.get('a.source_name', 'Unknown source'))
            date = article.get('published_at', article.get('a.publishedAt', 'No date'))
            content = article.get('content', article.get('a.full_content', 'No content available'))
            url = article.get('url', article.get('a.url', ''))

            # Highlight keywords in content
            highlighted_content = content
            if content:
                for keyword in keywords:
                    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                    highlighted_content = pattern.sub(f"**{keyword}**", highlighted_content)

            article_info = [
                f"📰 **{title}**",
                f"📅 Date: {date}",
                f"📍 Source: {source}",
                f"\n📝 Content: {highlighted_content[:500]}...",  # Show first 500 chars
            ]

            if url:
                article_info.append(f"\n🔗 [Read full article]({url})")

            response.append("\n".join(article_info))
            response.append("\n---\n")

        return "\n".join(response)

    except Exception as e:
        logging.error(f"Error querying knowledge graph: {e}")
        return f"Error querying knowledge graph: {str(e)}"


def get_bias_report(topic):
    """Get a report of bias across news sources on a topic"""
    try:
        if not kg:
            return "Sorry, the Knowledge Graph is not available right now."

        bias_report = kg.get_bias_report(topic, limit=10)

        if not bias_report:
            return f"No bias information found for topic: {topic}. Try a different topic or search term."

        # Format the results
        response = [f"# Bias Report: {topic}\n"]
        response.append("| News Source | Bias Assessment | Articles Analyzed |")
        response.append("|-------------|-----------------|-------------------|")

        for item in bias_report:
            source = item.get('source', 'Unknown')
            assessment = item.get('assessment', 'Neutral')
            count = item.get('article_count', 0)
            response.append(f"| {source} | {assessment} | {count} |")

        response.append("\n### Summary")
        response.append(
            f"Analysis based on {sum(item.get('article_count', 0) for item in bias_report)} articles across {len(bias_report)} sources.")

        return "\n".join(response)

    except Exception as e:
        logging.error(f"Error generating bias report: {e}")
        return f"Error generating bias report: {str(e)}"


def process_user_input(prompt):
    """Process user input to understand intent and generate appropriate response"""
    prompt_lower = prompt.lower()

    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in prompt_lower for greeting in greetings):
        if not st.session_state.conversation_context['greeted']:
            st.session_state.conversation_context['greeted'] = True
            return {
                'type': 'greeting',
                'response': f"{get_greeting()}! I'm your news analysis assistant powered by a Knowledge Graph. I can help you find articles, analyze bias, and fact-check claims. How can I assist you today?"
            }
        else:
            return {
                'type': 'greeting',
                'response': "Hello again! What topic would you like to explore today? I can search for news, analyze bias, or fact-check claims."
            }

    # Check for personal questions about the bot
    if 'who are you' in prompt_lower or 'what can you do' in prompt_lower:
        return {
            'type': 'introduction',
            'response': """I'm a news analysis assistant that uses a Knowledge Graph to understand connections between articles, people, and events. Here's what I can do:

1. 🔍 **Search for news articles** on specific topics
2. 📊 **Analyze bias** in news coverage
3. ✓ **Fact-check claims** against verified information
4. 🕸️ **Find connections** between news stories

Just ask me questions about news topics you're interested in!"""
        }

    # Check for thank you messages
    if 'thank' in prompt_lower or 'thanks' in prompt_lower:
        return {
            'type': 'gratitude',
            'response': "You're welcome! I'm happy to help. Feel free to ask if you have any other questions about news or current events."
        }

    # Check for goodbyes
    if 'bye' in prompt_lower or 'goodbye' in prompt_lower:
        return {
            'type': 'farewell',
            'response': "Goodbye! Feel free to come back anytime you need help understanding the news. Have a great day!"
        }

    # Check for bias analysis requests
    if 'bias' in prompt_lower or 'biased' in prompt_lower or 'leaning' in prompt_lower:
        if 'report' in prompt_lower or 'across' in prompt_lower or 'sources' in prompt_lower:
            # Extract topic for bias report
            keywords = extract_keywords(prompt)
            topic = ' '.join(keywords) if keywords else "politics"  # Default to politics if no keywords
            return {
                'type': 'bias_report',
                'response': get_bias_report(topic)
            }
        else:
            return {
                'type': 'bias_analysis',
                'response': process_bias_query(prompt)
            }

    # Check for fact-checking requests
    if 'fact' in prompt_lower or 'check' in prompt_lower or 'verify' in prompt_lower or 'true' in prompt_lower or 'false' in prompt_lower:
        return {
            'type': 'fact_check',
            'response': process_fact_check_query(prompt)
        }

    # Default to knowledge graph query
    return {
        'type': 'query',
        'response': query_knowledge_graph(prompt)
    }


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
analyze bias, and fact-check claims.
""")

# Sidebar with connection status
with st.sidebar:
    # Add connection status
    st.subheader("Connection Status")

    # Check Neo4j connection
    is_connected = test_neo4j_connection()
    if is_connected:
        st.success("✅ Connected to Knowledge Graph")
    else:
        st.error("❌ Not Connected to Knowledge Graph")

    # Check if KG is initialized
    if kg:
        st.success("✅ Knowledge Graph Initialized")
    else:
        st.error("❌ Knowledge Graph Not Initialized")

    # Check if LLM is available
    if llm:
        st.success("✅ LLM Ready")
    else:
        st.error("❌ LLM Not Available")

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
        greeting = f"{get_greeting()}! I'm your news analysis assistant. I can help you find articles, analyze bias, and fact-check claims. How can I help you today?"
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
        with st.spinner("Analyzing your request..."):
            processed = process_user_input(user_input)
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

    - **Search for articles**: "Find news about climate change"
    - **Analyze bias**: "Is there bias in coverage of the election?"
    - **Get bias reports**: "Show bias report for Ukraine conflict"
    - **Fact-check claims**: "Fact check: Did the president say taxes will increase?"

    ### Examples:
    - "Show me articles about technology"
    - "Is there bias in reporting on healthcare reform?"
    - "Fact check this claim: The economy grew by 5% last quarter"
    - "Generate a bias report on immigration news"
    """)

# About section
with st.sidebar.expander("ℹ️ About"):
    st.markdown("""
    This news analysis chatbot uses a Knowledge Graph to understand connections between articles, people, and events.

    It leverages:
    - **Neo4j** for graph database storage
    - **AWS Bedrock** for LLM capabilities
    - **Direct agent-KG interaction** for efficient processing

    The system can analyze bias, fact-check claims, and find relationships between news entities - all using a simplified architecture with direct KG interaction.
    """)