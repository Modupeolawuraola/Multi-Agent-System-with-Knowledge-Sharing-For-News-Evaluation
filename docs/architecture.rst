System Architecture
==================

Agent Structure
-------------
The system consists of seven specialized agents working together:

![multiagent-diagram_v3](https://github.com/user-attachments/assets/bb406a4a-0e7c-464a-8c91-30fd90d342ea)

1. **Agent 7 (User Interface Agent)**
    * Handles user queries
    * Manages existing knowledge checks
    * Returns final responses

2. **Agent 2 (Data Collection Agent)**
    * Retrieves fresh updates
    * Manages data collection
    * Processes new information

3. **Agent 3 & 4 (Analysis Agents)**
    * Performs bias analysis
    * Conducts fact-checking
    * Validates new data

4. **Agent 5 (Knowledge Graph Agent)**
    * Integrates verified data
    * Maintains knowledge graph
    * Updates relationships

5. **Agent 6 (Summarization Agent)**
    * Generates unbiased summaries
    * Processes multiple sources
    * Creates balanced perspectives

Workflow
--------
![project_KG_schema](https://github.com/user-attachments/assets/3a0c1cde-cd08-42c9-bdff-58ccf2b44d90)

1. User query → Agent 7
2. Knowledge check
3. Fresh data collection (if needed)
4. Bias and fact analysis
5. Knowledge graph integration
6. Summary generation
7. Response delivery

Tech Stack
---------
* **Backend:** Python, PyTorch
* **Frontend:** React
* **Database:** Neo4j
* **Tools & Libraries:**
    * PyTorch for machine learning
    * Neo4j for graph database
    * React for user interface