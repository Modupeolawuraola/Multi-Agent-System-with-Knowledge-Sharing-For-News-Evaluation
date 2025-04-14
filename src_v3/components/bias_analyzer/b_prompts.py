from langchain_core.prompts import ChatPromptTemplate

# Initial bias detection prompt
Bias_detection_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an expert at identifying political bias in news articles.
    Analyze this news article for potential bias indicators. Consider:
    - Narrative framing
    - Language patterns
    - Source Attribution
    - Emotional triggers
    - Compare the article to others with known bias in the available knowledge graph based on closely related nodes.
    - When making your determination please identify specific nodes in the knowledge graph that influenced your determination.

    - In your response return a single word to identify bias: "Left", "Right", or "Center" and the specific nodes in
    the knowledge graph. No other information is needed.
    """),
    ("user", """
    Analyze the following article for political bias. Use the given article text and contextual knowledge
    from similar articles in the knowledge graph.
    ARTICLE TEXT:
    {article_text}

    SIMILAR ARTICLES WITH KNOWN BIAS:
    {similar_articles_context}
    """)
])

# Deep analysis prompt
Deep_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    For each identified bias indicator, perform detailed analysis:
    - Context evaluation
    - Impact assessment
    - Alternative phrasings
    - Supporting evidence

    Provide specific examples from the text.
    """),
    ("user", "{detection_result}")
])

# Verify prompt
Verify_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Review the bias analysis and provide:
    - Confidence score (0-100)
    - Verification of each finding
    - Overall bias assessment
    - Recommendations for neutral alternatives

    Format as structured JSON:
    {
        "confidence_score": number,
        "findings": [list of verified findings],
        "overall_assessment": string,
        "recommendations": [list of recommendations]
    }
    """),
    ("user", "{analysis_result}")
])

BiasAnalysisSimplifiedPrompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are a political bias analyst tasked with determining the political bias of a news article.

        You are provided with:
        - The full text of the article.
        - A bias label from the most structurally similar article in a political knowledge graph
        - A list of entities (people, organizations, issues, etc.) that both articles mention

        Your task is to classify the **bias** of the article as one of:
        - "Left"
        - "Right"
        - "Center"
        
        Use the **bias label and entities** from the similar article as a clue — especially if they overlap with the current article — but do not rely on it exclusively. 
        Your final answer must consider the article’s framing, tone, and word choice. Use your own analysis of the article's text in combination with the knowledge graph context.
        - If applicable, include specific article titles, source names, or node types that contributed to your reasoning.

        Respond in JSON with this exact format:

        {{
            "bias": "Left" | "Right" | "Center",
            "confidence_score": 0-100,
            "reasoning": "Explain your determination briefly",
            "related_nodes": [list of article titles or node names used in comparison]
        }}
        """),
    ("user", """
    ARTICLE TEXT:
    {article_text}

    MOST SIMILAR ARTICLE BIAS:
    {similar_bias}

    SHARED ENTITIES:
    {matched_entities}
    """)
])