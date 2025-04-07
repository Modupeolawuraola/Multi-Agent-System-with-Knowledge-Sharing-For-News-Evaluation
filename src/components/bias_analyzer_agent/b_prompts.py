from langchain_core.prompts import ChatPromptTemplate

# Initial bias detection prompt
Bias_detection_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Analyze this news article for potential bias indicators. Consider:
    - Narrative framing
    - Language patterns
    - Source Attribution
    - Emotional triggers

    Identify specific examples of potential bias.
    """),
    ("user", "{article_text}")  # Fixed extra quote and comma
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