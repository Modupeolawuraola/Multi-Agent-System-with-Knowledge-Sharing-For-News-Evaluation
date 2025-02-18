
import pytest
from src.components.retriever_Agent.retriever_agent import RetrieverAgent
from src.components.updater_agent.updater_agent import UpdaterAgent  # Import directly from updater_agent.py
from src.memory.schema import GraphState
from datetime import datetime, timedelta

def test_retriever():
    """Test retriever functionality"""
    initial_state = GraphState(
        knowledge_graph={'articles': [
            {'title': 'Old Article', 'date': (datetime.now() - timedelta(days=2)).isoformat()},
            {'title': 'New Article', 'date': datetime.now().isoformat()},

        ]},
        last_retrieved_date=(datetime.now() - timedelta(days=1)).isoformat()
    )



    new_state = RetrieverAgent(initial_state)

    assert len(new_state['retrieved_articles'])== 1
    assert new_state['current_status'] == 'retrieval_complete'

def test_updater():
        """Test updater functionality"""
        initial_state =GraphState(
            knowledge_graph={'articles': []},
            retrieved_articles =[{'title': 'New Article'}],
            current_status='retrieval_complete')

        new_state= UpdaterAgent(initial_state)
        assert len(new_state['knowledge_graph']['articles']) == 1
        assert new_state['current_status'] == 'update_complete'
