

from langgraph.graph import StateGraph, END
from src_v3.memory.schema import GraphState
# from src_v3.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v3.components.bias_analyzer.bias_agent_update import bias_analyzer_agent
# from src_v3.components.fact_checker.fact_checker_Agent import fact_checker_agent
from src_v3.components.fact_checker.fact_checker_updated import fact_checker_agent
from src_v3.components.kg_builder.kg_builder import KnowledgeGraph
from src_v3.agent_manager.transistions import TransitionManager


class AgentManager:
    def __init__(self):
        """Initialize the agent manager with a state graph"""
        self.graph = StateGraph(GraphState)
        self.kg = KnowledgeGraph()

    def register_agents(self):
        """Register all agents as nodes"""
        # Define the node behavior to pass KG instance to agent functions
        self.graph.add_node('kg_builder', lambda state: self._kg_builder_node(state))
        self.graph.add_node('bias_analyzer', lambda state: self._bias_analyzer_node(state))
        self.graph.add_node('fact_checker', lambda state: self._fact_checker_node(state))
        self.graph.add_node('chatbot', lambda state: self._chatbot_node(state))

    def _kg_builder_node(self, state):
        """KG Builder just updates the Knowledge Graph from NewsAPI"""
        # Fetch articles from NewsAPI
        articles = self.kg.fetch_news_articles(query="politics", limit=10)

        # Add to KG (already happens in fetch_news_articles)
        state.message = f"Added {len(articles)} new articles to the Knowledge Graph."
        return state

    def _bias_analyzer_node(self, state):
        """Process a bias analysis request"""
        # Analyze either a direct query or related articles
        result_state = bias_analyzer_agent(state, self.kg)
        return result_state

    def _fact_checker_node(self, state):
        """Process a fact checking request"""
        # Verify either a direct query or article claims
        result_state = fact_checker_agent(state, self.kg)
        return result_state

    def _chatbot_node(self, state):
        """Process a user message and determine next steps"""
        user_message = state.user_message

        # Determine intent
        if "check fact" in user_message.lower() or "verify" in user_message.lower():
            state.news_query = user_message
            return state  # Will route to fact_checker

        elif "bias" in user_message.lower() or "leaning" in user_message.lower():
            state.bias_query = user_message
            return state  # Will route to bias_analyzer

        elif "update" in user_message.lower() or "news" in user_message.lower():
            # No specific query - will route to kg_builder
            return state

        else:
            # Generic response
            state.message = "I can check facts, analyze bias, or update the news database. How can I help you?"
            return state

    def define_workflow(self):
        """Define the workflow based on the new architecture"""
        # Chatbot is the entry point for user requests
        self.graph.add_conditional_edges(
            "chatbot",
            TransitionManager.determine_route_from_chatbot,
            {
                "kg_builder_path": "kg_builder",
                "bias_path": "bias_analyzer",
                "fact_check_path": "fact_checker",
                "end": END
            }
        )

        # All other agents return to END
        self.graph.add_edge("kg_builder", END)
        self.graph.add_edge("bias_analyzer", END)
        self.graph.add_edge("fact_checker", END)

    def process_user_message(self, message: str):
        """
        Process a user message and return a response

        Args:
            message: The user's message

        Returns:
            Response to the user
        """
        # Create workflow if not already created
        workflow = self.create_workflow()

        # Create initial state with user message
        initial_state = GraphState(
            user_message=message,
            current_status="ready"
        )

        # Run workflow
        final_state = workflow.invoke(initial_state)

        # Extract appropriate response based on which path was taken
        if hasattr(final_state, "fact_check_result") and final_state.fact_check_result:
            return self._format_fact_check_response(final_state.fact_check_result)

        elif hasattr(final_state, "bias_analysis_result") and final_state.bias_analysis_result:
            return self._format_bias_analysis_response(final_state.bias_analysis_result)

        elif hasattr(final_state, "message"):
            return final_state.message

        else:
            return "I've processed your request, but don't have a specific response to provide."

    def _format_fact_check_response(self, fact_check_result):
        """Format fact check results into a user-friendly response"""
        verified_claims = fact_check_result.get('verified_claims', [])

        if not verified_claims:
            return "I couldn't verify any specific claims in that statement."

        response = "Here's what I found:\n\n"

        for claim in verified_claims:
            verdict = claim.get('verification', {}).get('verdict', 'unknown')
            confidence = claim.get('verification', {}).get('confidence', 0)

            response += f"Claim: {claim.get('claim')}\n"
            response += f"Verdict: {verdict.capitalize()} (Confidence: {int(confidence * 100)}%)\n\n"

        return response

    def _format_bias_analysis_response(self, bias_result):
        """Format bias analysis results into a user-friendly response"""
        response = "Bias Analysis:\n\n"

        response += f"Overall Assessment: {bias_result.get('overall_assessment', 'Unknown')}\n"
        response += f"Confidence: {bias_result.get('confidence_score', 0)}%\n\n"

        if 'findings' in bias_result:
            response += "Key findings:\n"
            for finding in bias_result.get('findings', []):
                response += f"- {finding}\n"

        return response

    def create_workflow(self):
        """Create and return the complete workflow"""
        # Add a chatbot node as the main entry point
        self.graph.add_node("chatbot", self._chatbot_node)

        # Register other agent nodes
        self.register_agents()

        # Define workflow
        self.define_workflow()

        # Set entry point to chatbot
        self.graph.set_entry_point("chatbot")

        # Return compiled workflow
        return self.graph.compile()