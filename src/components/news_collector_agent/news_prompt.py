from langchain_core.prompts import ChatPromptTemplate

#prompt for generating search queries

query_generation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
        You are news collector assistant. Generate relevant search queries for the following topic.
        Focus on the factual and unbiased news  coverage.
        
        Format: return a list of 3-5 search queries that would help find comprehensive coverage.
        """),
        ("user", "{topic}")
    ]
)

#prompt for filtering relevant articles
article_filter_prompt =ChatPromptTemplate.from_messages([
    ("system", """
    Evaluate if this news article is relevant to our topic of interest.
    Consider:
    -Relevant to main topic
    -information value
    -Credibility of source
   
   Return a JSON with:
    {
    "is_relevant": boolean,
    "relevance_score":float(0-1),
    "reasoning": "brief explanation"
    }"""),
    ("user", """
    Topic:{topic}
    Article Title:{Title}
    article summary : {summary}
    source:{source}
    """)
])

#prompt for source validation
source_validation_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Evaluate the credibility of this news source.
    Consider:
    -Historical accuracy
    -Reporting standards
    -Known biases
    
    Return a JSON with:
    {
    "credibility_score":float(0-1),
    "known_biases":list,
    "recommendations":"use"/"verify"/"avoid"}
    """),
    ("user", "{source_name}")
])

