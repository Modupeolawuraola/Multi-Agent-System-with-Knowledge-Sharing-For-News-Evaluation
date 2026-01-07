Development Guide
================

Project Setup
-----------
1. Clone the repository with this repo link - https://github.com/Modupeolawuraola/Multi-Agent-System-with-Knowledge-Sharing-For-News-Evaluation
2. Install dependencies from requirements.txt
3. Set up Neo4j database
4. Configure environment variables
5. create a virtual environment  to connect with AWS Bedrock


Setup environment variables create .env file in the src directory with the following variables:

.. code-block:: text

    AWS_ACCESS_KEY_ID=your_aws_access_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret_key
    AWS_SESSION_TOKEN=your_aws_session_token
    AWS_REGION=us-east-1
    NEWS_API_KEY=your_news_api_key
    NEO4J_URI=your_neo4j_uri
    NEO4J_USERNAME=your_neo4j_username
    NEO4J_PASSWORD=your_neo4j_password

Running Different Systems
-------------------------

The repository includes three system implementations:

**LLM+KG System (Main)**

.. code-block:: bash

    python main.py

**RAG Baseline**

.. code-block:: bash

    # Install additional dependencies
    pip install chromadb sentence-transformers mistralai

    # Run RAG system
    python rag_baseline/run_rag.py

**LLM-Only Baseline**

.. code-block:: bash

    python llm_only_baseline/run_llm_only.py

Evaluation
----------

Run system evaluations:

**Bias Detection**

.. code-block:: bash

    # LLM+KG
    python sys_evaluation/evaluate_bias.py

    # RAG Baseline
    python sys_evaluation/evaluate_bias_rag.py

    # LLM-Only
    python sys_evaluation/evaluate_bias_llm_only.py

**Fact-Checking**

.. code-block:: bash

    # LLM+KG
    python sys_evaluation/evaluate_factcheck.py

    # RAG Baseline
    python sys_evaluation/evaluate_factcheck_rag.py

    # LLM-Only
    python sys_evaluation/evaluate_factcheck_llm_only.py

**Statistical Analysis**

.. code-block:: bash

    python sys_evaluation/statistical_tests.py


Testing
-------
* Unit Testing
* Integration Testing
* Performance Evaluation Testing
* Streamlit End-user Interface prompt Testing

Project Folder Structure
--------------
.. code-block:: text

    project_root/
    ├── src/
    │   ├── component/
    │   │   ├── bias_analyzer_agent/
    │   │   ├── fact_checker_agent/
    │   │   ├── KG Builder/
    │   │   └── agent_manager/
    │   │       ├── manager.py
    │   │       └── transistion.py
    │   ├── memory/
    │   │   ├── knowledge_graph/
    │   │   ├── schema/
    │   │   └── state/
    │   ├── util/
    │   │   └── aws_helperfunction/
    │   ├── workflow/
    │   │   ├── config.py
    │   │   ├── graph.py
    │   │   └── simplified_workflow/
    │   └── ui/
    │       └── streamlit/
    │           └── chatbot_ui.py
    │
    ├── system_evaluation/
    │   ├── result/
    │   ├── test_dataset/
    │   ├── evaluate.py
    │   ├── metrics_updated.py
    │   └── visualization_updated.py
    ├── unit_tests_v2/
    │   ├── test_api_keys.py
    │   ├── test_bias_analyzer.py
    │   ├── test_fact_checking.py
    │   ├── test_fact_kg_builder.py
    │   └── test_bedrock_setup.py
    ├── docs/
    ├── project_proposal/
    ├── research_paper/
    │   ├── latex/
    │   │   └── fig/
    │   └── word/
    ├── assets/
    │   └── fig/
    ├── reports/
    │   ├── latex_report/
    │   │   └── fig/
    │   ├── markdown_report/
    │   └── word_report/
    └── presentations/
        └── preliminary_findings/Development Guide
================

