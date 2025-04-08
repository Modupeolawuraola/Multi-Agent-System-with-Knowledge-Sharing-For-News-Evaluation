from langchain_core.prompts import ChatPromptTemplate

# Content summarization prompt
Content_summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert article summarizer. Your task is to:
    1. Identify the main topic and key points
    2. Extract important facts and figures
    3. Highlight significant quotes or statements
    4. Maintain the article's context and tone
    5. Provide a clear, concise summary

    Focus on accuracy and completeness while keeping the summary concise.
    """),
    ("user", "{article_text}")
])

# Relationship analysis prompt
Relationship_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert in analyzing relationships and connections in news articles.
    For the given article, identify and analyze:
    1. People:
       - Who are the key individuals mentioned?
       - What are their roles and relationships?
       - How are they connected to other entities?

    2. Organizations:
       - Which organizations are involved?
       - What are their relationships with other entities?
       - What roles do they play in the story?

    3. Events:
       - What events are described?
       - How do they connect to people and organizations?
       - What is their significance?

    4. Policies and Issues:
       - What policies or issues are discussed?
       - How do they relate to the other entities?
       - What are the key points of contention or agreement?

    5. Connections:
       - How do all these entities interact?
       - What are the key relationships?
       - What patterns or networks emerge?

    Provide a structured analysis that shows how these elements are interconnected.
    """),
    ("user", "{article_text}")
])

# Verification prompt
Verify_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Review the summaries and analysis and provide:
    1. Content Summary:
       - Main points covered
       - Key facts included
       - Important context preserved

    2. Relationship Analysis:
       - Entities identified
       - Connections verified
       - Network structure confirmed

    Format as structured JSON:
    {
        "content_summary": {
            "main_points": [list of points],
            "key_facts": [list of facts],
            "context": string
        },
        "relationship_analysis": {
            "entities": [list of entities],
            "connections": [list of connections],
            "network_structure": string
        }
    }
    """),
    ("user", "{analysis_result}")
]) 