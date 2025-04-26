System Architecture
==================

Agent Structure
-------------
The system consists of several components that work together:

- **Knowledge Graph** : A Neo4j-based dynamic knowledge repository that stores news articles and entity relationships
- **Specialized Agents** : Bias Analyzer Agent : Analyzes political news articles bias and leaning
- **Fact Checker Agent** : Verifies factual claims against knowledge graph context and internal knowledge
- **Agent Manager** :Orchestrates workflow between agents Routes user requests to appropriate processing paths Returns consolidated results to the user interface

Integration Framework:
- **GraphState Schema**: Standardized data structure for agent communication

- ***Streamlit UI***: User-friendly interface for interacting with the multi-agent system. This streamlined architecture enables efficient information sharing through the knowledge graph, allowing agents to leverage collaborative intelligence also maintaining specialized expertise in their respective domains.

Improved Multi-Agent Knowledge Sharing System

<img width="929" alt="Screenshot 2025-04-21 at 7 33 52 PM" src="https://github.com/user-attachments/assets/82179473-458b-4cb4-ac3d-64779b81b3fa" />

Workflow
--------

The system implement a flexible, knowledge -graph -centered architecture with specialized agents that operate independently but share information through a centralized knowledge repository.

- **Processing Route**:
The system supports three main processing routes:

1. **full-path** :Complete news analysis workflow
- Collects news from external sources
- Performs bias analysis and fact-checking
- Returns comprehensive analysis

2. **Fact-Check Path** : Direct claim verification
- Bypasses news collection and bias analysis
- Directly queries or updates knowledge graph with fact-check results
- Returns verification results with confidence scores


3. **Bias Analysis Path** : Focused bias assessment
- Skips news collection when analyzing specific content
- Updates knowledge graph with bias analysis
- Returns bias classification with supporting evidence



**Architecture Benefits**

- **Modular Design**: Agents function independently and can be developed/tested separately
- **Flexible Routing**: Multiple entry points based on user needs
- **Shared Knowledge**: Central knowledge graph eliminates redundant processing
- **Improved Performance**: Knowledge graph integration enhances accuracy compared to LLM-only approaches



**System Capabilities**

1. Fact-checking of direct user queries

2. Automated news collection and bias analysis

3. Persistent storage of analyzed articles in knowledge graph

4. Retrieval of balanced news perspectives

Knowledge Graph Workflow
-----------------------
Our system employs a dynamic knowledge graph for information storage and retrieval.

Tech Stack
---------
 **Large Language Models**: Claude 3 via AWS Bedrock
- **Knowledge Graph**: Neo4j
- **Backend**: Python
- **API Integration**: NewsAPI for article collection
- **Testing Framework**: Pytest
