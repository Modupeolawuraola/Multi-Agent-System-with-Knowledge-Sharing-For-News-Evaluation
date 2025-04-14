# import time
# import json
# import sys
# import os
# import logging
# from src_v3.utils.aws_helpers import diagnostic_check
#
# # Adding the root directory to the path to fix imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# # Import components
# from src_v3.memory.schema import GraphState
# from src_v3.memory.knowledge_graph import KnowledgeGraph  \
# from sys_evaluation.metrics_updated import (
#     calculate_bias_metrics,
#     calculate_fact_check_metrics
# )
# from sys_evaluation.visualization_updated import generate_evaluation_chart, plot_confusion_matrix
# from src_v3.workflow.simplified_workflow import process_articles
# from src_v3.utils.aws_helpers import get_bedrock_llm
# # Import for direct query route
# # from src_v3.components.fact_checker.fact_checker_updated import FactCheckerAgent, fact_checker_agent
#
# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("evaluation.log"),
#         logging.StreamHandler()
#     ]
# )
#
#
# def load_politifact_dataset():
#     """Load PolitiFact dataset for fact checking evaluation"""
#     import pandas as pd
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
#     DATASET_PATH = os.path.join(BASE_DIR, 'sys_evaluation', 'test_dataset', 'mini_fact_check_test.csv')
#
#     # Load from CSV file
#     df = pd.read_csv(DATASET_PATH)
#
#
#     test_claims = []
#     for _, row in df.iterrows():
#         claim = {
#             "claim": row['claim'],
#             "date": row['date'],
#             "ground_truth_verdict": row['rating']  # true, false, pants-fire, etc.
#         }
#         test_claims.append(claim)
#     return test_claims
