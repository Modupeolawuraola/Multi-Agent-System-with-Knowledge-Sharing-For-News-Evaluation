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
from src_v3.memory.knowledge_graph import KnowledgeGraph
from src_v3.components.bias_analyzer.bias_agent_update import bias_analyzer_agent
from src_v3.components.fact_checker.fact_checker_updated import fact_checker_agent
from src_v3.memory.schema import GraphState
from src_v3.utils.aws_helpers import get_bedrock_llm, test_neo4j_connection

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    logging.info("Attempting to initialize Knowledge Graph and LLM...")
    kg = KnowledgeGraph()
    llm = get_bedrock_llm()

    # Pre-initialize transformers for both agents
    from src_v3.components.fact_checker.tools import initialize_entity_extractor as init_fact_checker
    from src_v3.components.bias_analyzer.tools import initialize_entity_extractor as init_bias_analyzer

    init_fact_checker(llm)
    init_bias_analyzer(llm)

    logging.info("Knowledge Graph and Multi-Agent LLM initialized successfully")
except Exception as e:
    kg = None
    llm = None
    logging.error(f"Error initializing KG or Multi-Agent LLM: {e}")

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
    logging.debug(f"Extracting keywords from: {text}")
    # Remove common words and keep important ones
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was',
                    'show', 'me', 'find', 'search', 'get', 'about', 'of', 'with', 'by', 'from', 'up', 'down', 'what',
                    'articles', 'news', 'information', 'tell', 'give', 'generate', 'report', 'coverage', 'how'}

    # Split into words and remove punctuation
    words = re.findall(r'\w+', text.lower())
    # Filter out common words and short words (length < 2)
    keywords = [word for word in words if word not in common_words and len(word) > 2]
    logging.debug(f"Extracted keywords: {keywords}")
    return keywords if keywords else None


def populate_test_data():
    """Populate test data into the knowledge graph for demonstration"""
    if not kg:
        return False

    sample_articles = [
        {
            'title': 'Biden Administration Announces New Immigration Policy',
            'content': 'The Biden administration today unveiled a comprehensive immigration reform plan that aims to address border security while providing a path to citizenship for long-term residents. Critics argue the plan doesn\'t do enough to secure the border, while supporters praise its humanitarian approach.',
            'source': 'Political News Daily',
            'date': '2025-03-15T14:30:00Z',
            'url': 'https://example.com/biden-immigration-policy'
        },
        {
            'title': 'Supreme Court Rules on Major Voting Rights Case',
            'content': 'In a landmark 6-3 decision, the Supreme Court has upheld state laws requiring voter identification. Conservative justices cited election security concerns, while liberal justices dissented, arguing the laws disproportionately affect minority voters.',
            'source': 'Legal Affairs Today',
            'date': '2025-04-02T09:15:00Z',
            'url': 'https://example.com/supreme-court-voting-rights'
        },
        {
            'title': 'Trump Claims Economy Would Be Stronger Under His Leadership',
            'content': 'Former President Trump stated yesterday that economic indicators would be significantly better had he won the 2020 election. Economic experts disagree on this assessment, with some pointing to global factors affecting all economies regardless of leadership.',
            'source': 'Conservative Daily',
            'date': '2025-04-10T16:45:00Z',
            'url': 'https://example.com/trump-economy-claims'
        }
    ]

    # Add articles to the knowledge graph
    count = 0
    for article in sample_articles:
        if kg.add_article(article):
            # Add a bias analysis for demonstration
            bias_analysis = {
                'bias': 'Center' if 'Legal Affairs' in article['source'] else 'Right' if 'Conservative' in article[
                    'source'] else 'Left',
                'confidence_score': 75,
                'reasoning': f'Analysis of language, framing, and source reputation of {article["source"]}.'
            }
            try:
                # Call with only 2 parameters now
                kg.add_bias_analysis(article['url'], bias_analysis)
                count += 1
            except Exception as e:
                logging.error(f"Error adding bias analysis: {e}")

    return count > 0


def process_bias_query(query):
    """Process a query related to bias detection"""
    logging.info(f"BIAS ANALYSIS requested for: {query}")
    try:
        if not kg or not llm:
            logging.warning("KG or Multi-agent not available for bias analysis")
            return "Sorry, I can't analyze bias right now because the Knowledge Graph or Multi-agent is not available."

        # Create an initial state with the bias query
        state = GraphState(bias_query=query)
        logging.debug(f"Created GraphState for bias query: {state}")

        # Process with bias analyzer agent
        logging.info("Calling bias_analyzer_agent...")
        result_state = bias_analyzer_agent(state, kg)
        logging.info(f"Bias analyzer completed with status: {result_state.current_status}")
        logging.debug(f"Bias analyzer result: {result_state.model_dump()}")

        # Check for results in the expected location
        if result_state.articles and len(result_state.articles) > 0 and "bias_result" in result_state.articles[0]:
            logging.info("Bias result found in articles")
            # Try to parse the bias result if it's a JSON string
            bias_result = result_state.articles[0]["bias_result"]
            if isinstance(bias_result, str):
                try:
                    bias_data = json.loads(bias_result)
                    logging.debug(f"Parsed bias result JSON: {bias_data}")
                except json.JSONDecodeError as e:
                    logging.warning(f"Failed to parse bias result as JSON: {e}")
                    bias_data = {"bias": "Unknown", "confidence_score": 0, "reasoning": bias_result}
            else:
                bias_data = bias_result
                logging.debug(f"Using bias result as object: {bias_data}")

            # Format in a conversational style
            return f"""I've analyzed the bias in the content you asked about. 

The content appears to have a **{bias_data.get('bias', 'Unknown').upper()}** bias with a confidence score of **{bias_data.get('confidence_score', 0)}%**.

Here's my reasoning:
{bias_data.get('reasoning', 'No detailed explanation available.')}

The analysis considered these related points: {', '.join(bias_data.get('related_nodes', ['None identified']))}"""

        else:
            logging.warning("No bias result found in the returned state")
            return "I analyzed your query but couldn't determine any clear bias. This could be because the content is neutral or because there's not enough information to make a determination. Can you provide more details or a specific Political article to analyze?"

    except Exception as e:
        logging.error(f"Error in bias analysis: {e}", exc_info=True)
        return f"I ran into a problem while analyzing bias in that content. The system reported: {str(e)}. Would you like to try a different query?"


def process_fact_check_query(query):
    """Process a query related to fact checking"""
    logging.info(f"FACT CHECK requested for: {query}")
    try:
        if not kg or not llm:
            logging.warning("KG or Multi-Agent LLM not available for fact checking")
            return "Sorry, I can't fact-check right now because the Knowledge Graph or Multi-agent is not available."

        # Create an initial state with the news query
        state = GraphState(news_query=query)
        logging.debug(f"Created GraphState for fact check: {state}")

        # Process with fact checker agent - don't store in KG
        logging.info("Calling fact_checker_agent...")
        result_state = fact_checker_agent(state, kg, store_to_kg=False)
        logging.info(f"Fact checker completed with status: {result_state.current_status}")
        logging.debug(f"Fact checker result: {result_state.model_dump()}")

        # Check for results in articles first (new structure)
        if result_state.articles and len(result_state.articles) > 0 and "fact_check_result" in result_state.articles[0]:
            logging.info("Fact check result found in articles")
            result = result_state.articles[0]["fact_check_result"]
            logging.debug(f"Fact check result: {result}")

            # Format for chatbot - conversational style
            verdict = result.get('verdict', 'Unknown')
            confidence = result.get('confidence_score', 0)
            reasoning = result.get('reasoning', 'No detailed reasoning available')

            if verdict.lower() == 'true':
                verdict_icon = "✅"
                verdict_text = "TRUE"
            elif verdict.lower() == 'false':
                verdict_icon = "❌"
                verdict_text = "FALSE"
            else:
                verdict_icon = "⚠️"
                verdict_text = "UNCERTAIN"

            return f"""{verdict_icon} Based on my fact-checking, this claim appears to be **{verdict_text}**.

I'm **{confidence}%** confident in this assessment.

**Here's why:**
{reasoning}

This analysis is based on information from: {', '.join(result.get('supporting_nodes', ['available knowledge']))}"""
        else:
            logging.warning("No fact check result found in the returned state")
            return "I've looked into your claim, but I don't have enough information to verify it conclusively. Could you provide more specific details or rephrase your question?"

    except Exception as e:
        logging.error(f"Error in fact checking: {e}", exc_info=True)
        return f"I encountered a problem while trying to fact-check that. The system reported: {str(e)}. Would you like to try a different question?"


def query_knowledge_graph(query):
    """Query the knowledge graph for relevant articles"""
    logging.info(f"KNOWLEDGE GRAPH QUERY for: {query}")
    try:
        if not kg:
            logging.warning("KG not available for query")
            return "Sorry, the Knowledge Graph is not available right now."

        # Extract keywords for search
        keywords = extract_keywords(query)
        if not keywords:
            logging.warning("No keywords extracted from query")
            return "I'm not sure what specific news you're looking for. Could you try again with more specific terms? For example, 'Show me news about climate change' or 'Find articles about the Political'."

        # Check if we need to populate test data
        if not st.session_state.get('data_populated', False):
            data_added = populate_test_data()
            st.session_state.data_populated = True
            if data_added:
                logging.info("Added sample articles to Knowledge Graph for demonstration")

        # Get related articles from KG
        search_query = ' '.join(keywords)
        logging.info(f"Searching KG with query: {search_query}")
        articles = kg.retrieve_related_articles(search_query, limit=3)
        logging.info(f"Retrieved {len(articles) if articles else 0} articles from KG")

        if articles:
            logging.debug(f"First article: {articles[0]}")

        if not articles:
            logging.warning(f"No articles found for keywords: {keywords}")
            return f"I searched for news about {', '.join(keywords)}, but didn't find any matching articles. Would you like to try different search terms?"

        # Format the results in a conversational style
        response = []
        response.append(f"I found {len(articles)} articles about {', '.join(keywords)}. Here's a summary:")

        for i, article in enumerate(articles, 1):
            title = article.get('title', article.get('a.title', 'Untitled article'))
            source = article.get('source_name', article.get('a.source_name', 'Unknown source'))
            date = article.get('published_at', article.get('a.publishedAt', 'No date'))
            content = article.get('content', article.get('a.full_content', 'No content available'))
            url = article.get('url', article.get('a.url', ''))

            # Format date if possible
            try:
                if 'T' in date:
                    date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date = date_obj.strftime("%B %d, %Y")
            except Exception as e:
                logging.warning(f"Error formatting date: {e}")
                pass  # Keep original date format if parsing fails

            # Create a short summary - first 100 chars
            summary = content[:100] + "..." if len(content) > 100 else content

            response.append(f"\n**Article {i}: {title}**")
            response.append(f"Published by {source} on {date}")
            response.append(f"Summary: {summary}")

            if url:
                response.append(f"[Read the full article]({url})")

            response.append("")  # Empty line between articles

        response.append(
            "\nWould you like me to analyze the bias in any of these Political articles or fact-check a specific claim from them?")
        return "\n".join(response)

    except Exception as e:
        logging.error(f"Error querying knowledge graph: {e}", exc_info=True)
        return f"I had trouble searching for news about that topic. The system reported: {str(e)}. Would you like to try another search?"


def get_bias_report(topic):
    """Get a report of bias across news sources on a topic"""
    logging.info(f"BIAS REPORT requested for topic: {topic}")
    try:
        if not kg:
            logging.warning("KG not available for bias report")
            return "Sorry, the Knowledge Graph is not available right now."

        # Check if we need to populate test data
        if not st.session_state.get('data_populated', False):
            data_added = populate_test_data()
            st.session_state.data_populated = True
            if data_added:
                logging.info("Added sample articles to Knowledge Graph for demonstration")

        # Strip unnecessary words for better search results
        clean_topic = ' '.join(extract_keywords(topic) or ['politics'])
        logging.info(f"Cleaned bias report topic: {clean_topic}")

        try:
            logging.info(f"Calling KG get_bias_report for Political topic: {clean_topic}")
            bias_report = kg.get_bias_report(clean_topic, limit=5)
            logging.info(f"Retrieved bias report with {len(bias_report) if bias_report else 0} sources")
        except Exception as e:
            logging.error(f"Error in get_bias_report: {e}")
            # Fallback to mock data for demonstration
            bias_report = [
                {"source": "Conservative News", "assessment": "Right", "article_count": 5},
                {"source": "Progressive Daily", "assessment": "Left", "article_count": 4},
                {"source": "Political News Daily", "assessment": "Center", "article_count": 7}
            ]
            logging.info("Using fallback mock data for bias report")

        if bias_report:
            logging.debug(f"First bias report item: {bias_report[0]}")

        if not bias_report:
            logging.warning(f"No bias report found for topic: {topic}")
            return f"I don't have enough information to create a bias Political report on '{topic}'. This might be because there aren't enough articles on this topic in my knowledge base. Would you like to search for news on this topic instead?"

        # Format the results in a conversational style
        response = [f"Here's my bias analysis for Political news coverage about **{topic}**:"]

        left_sources = []
        center_sources = []
        right_sources = []

        for item in bias_report:
            source = item.get('source', 'Unknown')
            assessment = item.get('assessment', 'Neutral').lower()

            if "left" in assessment:
                left_sources.append(source)
            elif "right" in assessment:
                right_sources.append(source)
            else:
                center_sources.append(source)

        if left_sources:
            response.append(f"\n**Left-leaning sources:** {', '.join(left_sources)}")

        if center_sources:
            response.append(f"\n**Center/Neutral sources:** {', '.join(center_sources)}")

        if right_sources:
            response.append(f"\n**Right-leaning sources:** {', '.join(right_sources)}")

        total_articles = sum(item.get('article_count', 0) for item in bias_report)
        response.append(
            f"\nThis analysis is based on {total_articles} articles from {len(bias_report)} different sources.")
        response.append(
            "\nWould you like me to look up specific articles on this topic or analyze the bias in a particular claim?")

        return "\n".join(response)

    except Exception as e:
        logging.error(f"Error generating bias report: {e}", exc_info=True)
        return f"I ran into a problem while creating a bias report on '{topic}'. The system reported: {str(e)}. Would you like to try a different Political topic?"


def process_user_input(prompt):
    """Process user input to understand intent and generate appropriate response"""
    logging.info(f"Processing user input: {prompt}")
    prompt_lower = prompt.lower()

    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in prompt_lower for greeting in greetings):
        logging.info("Identified as GREETING")
        if not st.session_state.conversation_context['greeted']:
            st.session_state.conversation_context['greeted'] = True
            return {
                'type': 'greeting',
                'response': f"{get_greeting()}! I'm your news analysis assistant powered by a Knowledge Graph. I can help you find articles, analyze bias, and fact-check claims. How can I assist you today?"
            }
        else:
            return {
                'type': 'greeting',
                'response': "Hello again! What topic would you like to explore today in Political world? I can search for news, analyze bias, or fact-check claims."
            }

    # Check for personal questions about the bot
    if 'who are you' in prompt_lower or 'what can you do' in prompt_lower:
        logging.info("Identified as INTRODUCTION question")
        return {
            'type': 'introduction',
            'response': """I'm a news analysis assistant that uses a Knowledge Graph to understand connections between articles, people, and events. Here's what I can do:

1. 🔍 **Search for news articles** on specific Political topics
2. 📊 **Analyze bias** in Political news coverage
3. ✓ **Fact-check claims** against verified information
4. 🕸️ **Find connections** between Political news stories

Just ask me questions about Political news topics you're interested in!"""
        }

    # Check for thank you messages
    if 'thank' in prompt_lower or 'thanks' in prompt_lower:
        logging.info("Identified as GRATITUDE")
        return {
            'type': 'gratitude',
            'response': "You're welcome! I'm happy to help. Feel free to ask if you have any other questions about Political news or current events."
        }

    # Check for goodbyes
    if 'bye' in prompt_lower or 'goodbye' in prompt_lower:
        logging.info("Identified as FAREWELL")
        return {
            'type': 'farewell',
            'response': "Goodbye! Feel free to come back anytime you need help understanding the news. Have a great day!"
        }

    # Check for bias analysis requests
    if 'bias' in prompt_lower or 'biased' in prompt_lower or 'leaning' in prompt_lower:
        if 'report' in prompt_lower or 'across' in prompt_lower or 'sources' in prompt_lower:
            logging.info("Identified as BIAS REPORT request")
            # Extract topic for bias report
            keywords = extract_keywords(prompt)
            topic = ' '.join(keywords) if keywords else "politics"  # Default to politics if no keywords
            logging.info(f"Getting bias report for topic: {topic}")
            return {
                'type': 'bias_report',
                'response': get_bias_report(topic)
            }
        else:
            logging.info("Identified as BIAS ANALYSIS request")
            return {
                'type': 'bias_analysis',
                'response': process_bias_query(prompt)
            }

    # Check for fact-checking requests
    if 'fact' in prompt_lower or 'check' in prompt_lower or 'verify' in prompt_lower or 'true' in prompt_lower or 'false' in prompt_lower or 'did' in prompt_lower:
        logging.info("Identified as FACT CHECK request")
        return {
            'type': 'fact_check',
            'response': process_fact_check_query(prompt)
        }

    # Default to knowledge graph query
    logging.info("Defaulting to KNOWLEDGE GRAPH query")
    return {
        'type': 'query',
        'response': query_knowledge_graph(prompt)
    }


# Set page config
st.set_page_config(
    page_title="Multi-Agent Knowledge Sharing System",
    page_icon="📰",
    layout="wide"
)

# Header
st.title("📰 Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs")
st.markdown("""
I'm your intelligent news assistant for bias detection and fact-checking. I can help you understand Political news articles, 
find connections between Political events, analyze media bias, and verify factual claims.
""")

# Sidebar with connection status
with st.sidebar:
    # Add connection status
    st.subheader("System Status")

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
        st.success("✅ Multi-Agent Ready")
    else:
        st.error("❌ Multi-Agent Not Available")

    # Add a load sample data button for demonstration
    if st.button("Load Sample Data"):
        with st.spinner("Loading sample articles..."):
            success = populate_test_data()
            if success:
                st.session_state.data_populated = True
                st.success("✅ Sample articles loaded!")
            else:
                st.error("❌ Failed to load sample data")

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
        greeting = f"{get_greeting()}! I'm your news analysis assistant. I can help you find Political articles, analyze bias, and fact-check claims. How can I help you today?"
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})

# User input
if user_input := st.chat_input("Ask me about the Political news:"):
    # Log the input and add to chat history
    logging.info(f"Received user input: {user_input}")
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process the input and get response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            logging.info("Processing user input...")
            processed = process_user_input(user_input)
            response = processed['response']
            logging.info(f"Response type: {processed['type']}")
            logging.debug(f"Full response: {response[:100]}...")

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Add a clear chat button
if st.sidebar.button("Clear Chat"):
    logging.info("Clearing chat history")
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

    - **Search for articles**: "Find news about world politics"
    - **Analyze bias**: "Is there bias in coverage of the USA election?"
    - **Get bias reports**: "Show bias report for Ukraine conflict"
    - **Fact-check claims**: "Fact check: Did President Trump say taxes will increase?"

    ### Examples:
    - "Show me articles about United States politics"
    - "Is there bias in reporting on Trump news"
    - "Fact check this claim: Is Trump's approval rating more than 54%?"
    - "Generate a bias report on immigration"
    """)

# About section
with st.sidebar.expander("ℹ️ About"):
    st.markdown("""
    This multi-agent knowledge sharing system uses Dynamic Knowledge Graphs to understand connections between news articles, people, and events.

    It leverages:
    - **Neo4j** for graph database storage
    - **AWS Bedrock** for Multi-agent LLM capabilities
    - **Multi-agent architecture** for specialized analysis
    - **Dynamic Knowledge Graph** for evolving information

    The system specializes in bias detection and fact-checking through a unified architecture that enables intelligent processing of news content.
    """)