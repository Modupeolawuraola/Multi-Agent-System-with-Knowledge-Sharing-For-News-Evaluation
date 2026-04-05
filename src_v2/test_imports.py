import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Test imports one by one
try:
    from langchain_neo4j import Neo4jGraph
    logger.info("✅ Neo4jGraph import successful")
except ImportError as e:
    logger.error(f"❌ Neo4jGraph import failed: {e}")

try:
    from langchain_core.prompts import ChatPromptTemplate
    logger.info("✅ ChatPromptTemplate import successful")
except ImportError as e:
    logger.error(f"❌ ChatPromptTemplate import failed: {e}")

try:
    from langchain_aws import ChatBedrock
    logger.info("✅ ChatBedrock import successful")
except ImportError as e:
    logger.error(f"❌ ChatBedrock import failed: {e}")

try:
    from src_v2.utils.aws_helpers import get_aws_credentials, diagnostic_check
    logger.info("✅ aws_helpers import successful")
except ImportError as e:
    logger.error(f"❌ aws_helpers import failed: {e}")

try:
    from src_v2.components.summarizer.tools import create_summarization_chain, format_article
    logger.info("✅ summarizer tools import successful")
except ImportError as e:
    logger.error(f"❌ summarizer tools import failed: {e}")

# Try to import GraphState from different locations
try:
    from src.memory.schema import GraphState
    logger.info("✅ GraphState import from src.memory.schema successful")
except ImportError as e:
    logger.error(f"❌ GraphState import from src.memory.schema failed: {e}")

try:
    from src_v2.memory.schema import GraphState
    logger.info("✅ GraphState import from src_v2.memory.schema successful")
except ImportError as e:
    logger.error(f"❌ GraphState import from src_v2.memory.schema failed: {e}")

# Print Python path for debugging
logger.info("Python path:")
for path in sys.path:
    logger.info(f"  - {path}") 