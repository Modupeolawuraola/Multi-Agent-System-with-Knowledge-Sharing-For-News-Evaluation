System Architecture
==================

Agent Structure
-------------
The system architectural design consists of several components that works in collaboration:

- **Knowledge Graph**: A Neo4j-based dynamic knowledge graph that stores news articles and entity relationships
- **Specialized Agents**:
  - **Bias Analyzer Agent**: Analyzes political news articles bias and leaning
  - **Fact Checker Agent**: functions in verification of factual claims against knowledge graph context and internal knowledge
- **Agent Manager**: Orchestrates workflow between agents, routes user requests/query to appropriate processing paths/channel, returns consolidated and results to the user interface

Integration Framework:
- **GraphState Schema**: Standardized data structure for agent communication
- **Streamlit UI**: User-friendly interface for interacting with the multi-agent-KG system. This streamlined architecture enables efficient information sharing through the knowledge graph, allowing agents to leverage collaborative in storage intelligence while maintaining specialized expertise in their respective domains.

 System Architecture diagram
.. figure:: _static/images/architecture.png
   :alt: System Architecture Diagram
   :width: 800px




Workflow
--------

The system implements a flexible, knowledge-graph-centered architecture with specialized agents that operate independently but share information through a centralized knowledge graph.

- **Processing Route**:
The system supports three processing routes based on the algorithm below:

Main Processing Route of the System

.. figure:: _static/images/system_workflow.jpeg
   :alt: System Workflow
   :width: 800px




Knowledge Graph Workflow
-----------------------
Our system employs a dynamic knowledge graph for information storage and retrieval.

   Knowledge graph initialization and workflow

.. figure:: _static/images/kg_intialization.jpeg
   :alt: Knowledge Graph Initialization
   :width: 800px



.. figure:: _static/images/graph_copy.png
   :alt: Knowledge Graph Structure
   :width: 800px

   Knowledge graph structure and relationships

User Interface
-------------

The system provides an intuitive user interface for interacting with the multi-agent system:

Streamlit user interface for the multi-agent system

.. figure:: _static/images/ui1.png
   :alt: User Interface
   :width: 800px

.. figure:: _static/images/ui2.png
   :alt: User Interface
   :width: 800px

**Architecture Benefits**

- **Modular Design**: Agents independently functions, interact with KG and can be developed/tested separately
- **Flexible Routing**: The system has multiple entry points based on user needs
- **Shared Knowledge**: Central knowledge graph eliminates redundant processing
- **Improved Performance**: Knowledge graph integration enhances accuracy compared to LLM-only approaches


**System Capabilities**

1. Fact-checking of direct user queries
2. Automated news collection and bias analysis
3. Persistent storage of analyzed articles in knowledge graph
4. Retrieval of balanced news perspectives


Tech Stack
---------
- **Large Language Models**: Claude 3 via AWS Bedrock
- **Knowledge Graph**: Neo4j
- **Backend**: Python
- **API Integration**: NewsAPI for article collection
- **Testing Framework**: Pytest