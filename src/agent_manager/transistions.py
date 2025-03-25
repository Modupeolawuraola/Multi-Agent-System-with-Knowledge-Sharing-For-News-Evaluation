from typing import Callable, Dict, List
from ..memory.schema import GraphState


class TransitionManager:
    @staticmethod
    def route_after_bias_analysis(state: GraphState) -> str:
        """
        Determine where to route after bias analysis

        Args:
            state: Current graph state

        Returns:
            Next node name to route to
        """
        # Get current status
        status = state.get('current_status', '')

        # Check for errors
        if 'error' in status:
            return "updater"  # Even on error, proceed to update KG

        # Normal flow - go to fact checker
        return "updater"

    @staticmethod
    def route_after_fact_check(state: GraphState) -> str:
        """
        Determine where to route after fact checking

        Args:
            state: Current graph state

        Returns:
            Next node name to route to
        """
        # Check if we have direct query results
        if 'fact_check_result' in state:
            # This was a direct query - go to end
            return "END"

        # Normal flow with articles - go to updater
        return "updater"

    @staticmethod
    def should_update_kg(state: GraphState) -> bool:
        """
        Determine if knowledge graph should be updated

        Args:
            state: Current graph state

        Returns:
            Boolean indicating whether to update KG
        """
        # Check if we have articles to update
        if state.get('articles') and len(state.get('articles', [])) > 0:
            return True

        return False