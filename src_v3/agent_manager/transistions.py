from src_v3.memory.schema import GraphState


class TransitionManager:
    @staticmethod
    def determine_route_from_chatbot(state: GraphState) -> str:
        """
        Determine where to route after chatbot processing

        Args:
            state: Current graph state

        Returns:
            Path name to use
        """
        # Direct fact-checking query
        if state.news_query:
            return "fact_check_path"

        # Direct bias analysis query
        if state.bias_query:
            return "bias_path"

        # Update news request
        if "update" in state.user_message.lower() or "news" in state.user_message.lower():
            return "kg_builder_path"

        # No specific action needed - just return chatbot response
        return "end"