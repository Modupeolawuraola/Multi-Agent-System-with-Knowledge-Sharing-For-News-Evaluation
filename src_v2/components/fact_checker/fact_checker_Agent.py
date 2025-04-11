from typing import List, Dict, Any
from datetime import datetime
import json
from src_v2.memory.schema import GraphState, NewsArticle
from .tools import FactCheckTools
from src_v2.utils.aws_helpers import get_bedrock_llm
import logging

class FactCheckerAgent:
    """
    Agent responsible for fact-checking news articles by extracting claims,
    verifying them against reliable sources, and providing an overall assessment.
    """

    def __init__(self, llm, kg=None):
        """
        Initialize the fact checker agent.

        Args:
            llm: Language model for reasoning about claims and evidence
            kg: Knowledge Graph instance for direct interaction
        """
        self.llm = llm
        self.tools = FactCheckTools(knowledge_graph=kg)
        self.kg= kg #store the KG reference

    def extract_claims(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract factual claims from a news article or query.

        Args:
            article: News article dict containing title, content, etc.

        Returns:
            List of extracted claims as dictionaries
        """

        if not isinstance(article, dict):
            logging.error(f"Article is not a dictionary: {type(article)}")
            return []

        if 'content' not in article:
            logging.warning(f"Article missing 'content' field: {article.get('title', 'Unknown')}")
            return []
        # Prepare article content
        article_text = f"Title: {article.get('title', '')}\n\nContent: {article.get('content', '')}"

        # Direct prompt construction
        system_message = """You are a fact-checking assistant with expertise in identifying factual claims within news articles.
        Extract the key factual claims that can be verified from the article text.
        Focus on specific, verifiable assertions rather than opinions or subjective statements.

        For each claim:
        1. Extract the exact claim as stated in the article
        2. Identify entities involved (people, organizations, places)
        3. Categorize it (e.g., statistical, historical, causal, quotation)
        4. Assess the importance to the article's main points

        Return ONLY a JSON object with this exact format:
        {"claims": [{"claim": "exact claim text", "entities": ["entity1", "entity2"], "category": "category", "importance": number}]}

        Extract 3-7 of the most important verifiable claims from the article."""

        user_message = article_text

        # Use LLM to extract claims
        response = self.llm.invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        try:
            # Parse the JSON response
            claims = json.loads(response.content)
            return claims.get('claims', [])
        except Exception as e:
            print(f"Error extracting claims: {e}")
            return []

    def verify_claim_with_evidence(self, claim_text: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a single claim based on the collected evidence.

        Args:
            claim_text: The claim to verify
            evidence: List of evidence items collected from various sources

        Returns:
            Verification result with confidence and reasoning
        """
        # Direct prompt construction
        system_message = """You are a fact-checking assistant with expertise in evaluating evidence.
        Your task is to assess whether the provided evidence confirms, contradicts, or is insufficient to verify the claim.
        Carefully weigh the reliability and relevance of each piece of evidence.
        Consider the credibility of the sources and consistency across multiple sources.

        Return ONLY a JSON object with this exact format:
        {
            "is_verified": true/false,
            "confidence": 0.0-1.0,
            "verdict": "confirmed/refuted/partially_true/insufficient_evidence",
            "reasoning": "detailed explanation of how the evidence supports the verdict",
            "evidence_quality": 0.0-1.0,
            "evidence_reliability": 0.0-1.0,
            "contradicting_evidence": "any contradicting information found",
            "corroborating_sources": ["list of sources that confirm the claim"],
            "refuting_sources": ["list of sources that contradict the claim"]
        }"""

        user_message = f"""Claim to verify: {claim_text}

        Evidence found:
        {json.dumps(evidence, indent=2)}"""

        # Evaluate evidence against claim
        response = self.llm.invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        try:
            # Parse the verification result
            verification = json.loads(response.content)
            return verification
        except Exception as e:
            print(f"Error verifying claim: {e}")
            return {
                'is_verified': False,
                'confidence': 0.0,
                'verdict': 'error',
                'reasoning': f"Error in verification process: {str(e)}",
                'evidence_quality': 0.0,
                'evidence_reliability': 0.0
            }

    def verify_claims(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verify each claim by searching for evidence and evaluating it.
        """
        verified_claims = []

        # ADD THIS CHECK to handle empty claims
        if not claims:
            return []

        for claim in claims:
            claim_text = claim.get('claim', '')
            if not claim_text:
                continue

            # Search for evidence using tools - now includes multiple sources
            evidence = self.tools.search_for_evidence(claim_text)

            # ADD THIS CHECK to handle None evidence
            if evidence is None:
                evidence = []

            # Verify the claim with the collected evidence
            verification = self.verify_claim_with_evidence(claim_text, evidence)

            verified_claims.append({
                'claim': claim_text,
                'entities': claim.get('entities', []),
                'category': claim.get('category', ''),
                'importance': claim.get('importance', 5),
                'evidence': evidence,
                'verification': verification
            })

        return verified_claims

    def generate_fact_check_report(self, article: Dict[str, Any], verified_claims: List[Dict[str, Any]]) -> Dict[
        str, Any]:
        """
        Generate an overall fact-check report for the article.

        Args:
            article: Original news article
            verified_claims: List of verified claims with evidence

        Returns:
            Fact-check report dictionary
        """
        # Direct prompt construction
        system_message = """You are a fact-checking assistant with expertise in analyzing news articles for accuracy.
        Your task is to provide an overall assessment of the article's factual accuracy based on the verification of its key claims.
        Consider the importance of each claim, the confidence in verification, and patterns of inaccuracy.
        Also analyze source credibility and the quality of the evidence found.

        Return ONLY a JSON object with this exact format:
        {
            "overall_accuracy": 0.0-1.0,
            "overall_verdict": "accurate/mostly_accurate/mixed/mostly_inaccurate/inaccurate",
            "reasoning": "detailed explanation of the assessment",
            "key_issues": ["specific issues found"],
            "strongest_claims": ["claims with strong evidence"],
            "weakest_claims": ["claims with weak or contradictory evidence"],
            "missing_context": "important context that the article omits",
            "source_credibility": 0.0-1.0,
            "evidence_strength": 0.0-1.0,
            "recommendations": "recommendations for the reader",
            "misinformation_patterns": ["any patterns of misinformation detected"]
        }"""

        user_message = f"""Article Title: {article.get('title', '')}
        Article Source: {article.get('source', '')}

        Verified Claims:
        {json.dumps(verified_claims, indent=2)}"""

        response = self.llm.invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        try:
            # Parse the overall report
            report = json.loads(response.content)
            return report
        except Exception as e:
            print(f"Error generating fact-check report: {e}")
            return {
                'overall_accuracy': 0.0,
                'overall_verdict': 'Could not determine due to error',
                'reasoning': f"Error in report generation: {str(e)}",
                'source_credibility': 0.0,
                'evidence_strength': 0.0
            }


def fact_checker_agent(state: GraphState, knowledge_graph) -> GraphState:
    """Update fact checker agent that directly interacts with the knowledge graph.

    Args:
        state:current system state
        knowledge_graph:knowledgeGraph instance for direct interaction
        """



    if isinstance(state, dict):
        state=GraphState(**state)

    new_state = state.copy()

    # Get the AWS Bedrock LLM - no fallback to mock
    llm = get_bedrock_llm()

    news_query = state.news_query

    if news_query:
        # Direct user query processing path
        try:
            fact_checker = FactCheckerAgent(llm, kg=knowledge_graph)

            # Create a temporary article from the query
            temp_article = {
                'title': news_query[:50],  # Use first 50 chars as title
                'content': news_query,
                'source': 'user_query',
                'date': datetime.now().isoformat()
            }

            # First check if similar news exists in knowledge graph
            matched_articles = []
            if knowledge_graph:
                # Use KG's retrieve function directly instead of GraphState
                matched_articles = knowledge_graph.retrieve_related_articles(query=news_query, limit=5)

            # Extract and verify claims regardless of KG match
            claims = fact_checker.extract_claims(temp_article)
            verified_claims = fact_checker.verify_claims(claims)
            report = fact_checker.generate_fact_check_report(temp_article, verified_claims)

            # Prepare the verification result
            verification_status = {
                'status': 'verified' if verified_claims else 'unverified',
                'verified_claims': verified_claims,
                'report': report,
                'matched_knowledge_graph': len(matched_articles) > 0,
                'matched_articles': matched_articles if matched_articles else [],
                'timestamp': datetime.now().isoformat()
            }

            # Add verification result to state
            new_state.fact_check_result = verification_status
            new_state.current_status = 'fact_check_complete'

            # Store the fact check in the knowledge graph

            if knowledge_graph and verified_claims:

                for claim in verified_claims:
                    fact_checker.tools.store_fact_check_in_kg(

                        claim.get('claim', ''),

                        claim.get('verification', {})

                    )


        except Exception as e:

            print(f"Error in fact checking query: {e}")

            new_state.current_status = 'error: fact_checking_failed'

            new_state.error = str(e)

            new_state.fact_check_result = {

                'status': 'error',

                'message': f'Error during fact checking: {str(e)}',

                'timestamp': datetime.now().isoformat()

            }

        return new_state

    # Process articles if no direct query but articles exist
    articles_to_check = []
    if hasattr(state, "articles") and isinstance(state.articles, list):
        articles_to_check = state.articles
    elif hasattr(state, "article") and isinstance(state.article, list):
        # for backward compatibility
        articles_to_check = state.article

    # store in state using the standard articles key
    new_state.articles = articles_to_check.copy()

    if not articles_to_check:
        new_state.current_status = 'no_articles_to_fact_check'
        return new_state

    try:
        fact_checker = FactCheckerAgent(llm)

        # Process each article
        for i, article in enumerate(articles_to_check):
            # Skip articles that have already been fact-checked
            if article.get('fact_check'):
                continue

            # Extract claims
            claims = fact_checker.extract_claims(article)

            # Verify claims
            verified_claims = fact_checker.verify_claims(claims)

            # Generate overall report
            fact_check_report = fact_checker.generate_fact_check_report(article, verified_claims)

            # Add fact check results to article
            articles_to_check[i]['fact_check'] = {
                'verified_claims': verified_claims,
                'report': fact_check_report,
                'timestamp': datetime.now().isoformat()
            }

        # Update state
        new_state.articles = articles_to_check
        new_state.current_status = 'fact_check_complete'

    except Exception as e:
        print(f"Error in fact checking: {e}")
        new_state.current_status = 'error: fact_checking_failed'
        new_state.error = str(e)

    return new_state

