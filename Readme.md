## Project: Group 6: Improved Multi-Agent Knowledge Sharing Systems
## Title: Improved  Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs for News Bias Detection and Fact-Checking

Proposed by Group Initiative and Idea 

## Project Objectives:
The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased and fact-check of News topics/Articles. This project will explore the effects of shared memory on a multi-agent system and look at utilizing dynamic knowledge graphs to improve the overall efficiency of the system and accuracy of predictions and quality of  News. Specifically, this project will focus on:

Developing several agents based on customizing open-source LLMs for specific tasks, such as bias detection, Fact-checking, knowledge graph maintenance, data collection, and chat functionality.
Evaluating the effect of shared memory on a multi agent system, specifically focusing on the effect of deploying dynamic knowledge graphs compared to other methods. Evaluation metrics will focus on comparing compute resources, reducing redundancy of collected information, accuracy of bias classification and fact-checking, for quality of news.


## System Architecture
 
![multiagent-diagram_v3](https://github.com/user-attachments/assets/bb406a4a-0e7c-464a-8c91-30fd90d342ea)

![image](https://github.com/user-attachments/assets/019606a0-2dae-4edc-a896-ae76a23aec76)


## System Architecture Workflow/Interaction Diagram:

##  Agent Workflow Routes

# Route 1: Direct Query Processing

User: User provides a specific claim or article query to Agent 5

Agent 5: Fact Checker Agent: Checks knowledge graph for existing fact checks, Performs new fact-checking analysis if needed; Returns verified facts to the user

# Route 2: News Collection and Bias Analysis

Agent 1: News Collector Agent: Collects political news(spefics) from NewsAPI ; Passes collected articles to Bias Analyzer

Agent 2: Bias Analyzer Agent : Analyzes bias in news articles; Verifies claims; Classifies articles as biased or unbiased; Passes analyzed articles to Updater Agent

Agent 3: Updater Agent:  Integrates analyzed news articles into knowledge graph; Stores bias analysis results

Agent 4: Retriever Agent: Retrieves balanced information from knowledge graph ; Generates summaries with bias trends and balanced perspectives: Returns comprehensive analysis to user


System Capabilities
1. Fact-checking of direct user queries
2. Automated news collection and bias analysis
3. Persistent storage of analyzed articles in knowledge graph
4. Retrieval of balanced news perspectives




```bash
```
## Knowledge Graph WorkFlow

Structure:
![project_KG_schema](https://github.com/user-attachments/assets/3a0c1cde-cd08-42c9-bdff-58ccf2b44d90)

## Tech Stack:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Pytorch-%23FF6F00.svg?style=for-the-badge&logo=Pytorch&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-3670A0?style=for-the-badge&logo=Neo4j&logoColor=ffdd54)
![Pytorch](https://img.shields.io/badge/Sql-%23FF6F00.svg?style=for-the-badge&logo=Sql&logoColor=white)
![React](https://img.shields.io/badge/Docker-%2320232a.svg?style=for-the-badge&logo=Docker&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Aws-%23FF6F00.svg?style=for-the-badge&logo=Aws&logoColor=white)


## Project Approach:
The project will proceed in several phases:

Requirement Analysis: Collaborate with lead researchers to define key components of News knowledge sharing experiences and specify chatbot performance requirements.
## Technical Phase 

1. Week1. Environment Setup and technology stack Selection
      - Setup Tech stack environment
      -  Choose LLM frameworks
      - select graph database
      - Setup project documentation 
2. Week2: Basic agent framework Implementation /Data collection 
      - Implement basic agent communication 
      - Create Basic UI prototype
      -  Setup testing environment 
      - News article scrapping/Data preprocessing/API Integration
3. Week 3: Knowledge Graph Agent 
      - Graph database setup
      - Entity Extraction 
      - Relationship Mapping 
      - Dynamic update mechanism
4. Week4: Basic Agent communication 
      - Inter-agent messaging
      - Memory sharing implementation
      - State Management 
5. Week5: Specialized Agent Development(Bias and Summarization Agent)
      - Bias Detection Agent 
      - Bias detection models
      - Pattern recognition
      - Source Credibility analysis
      - Contextual analysis
      - Text Summarization models 
      - Bias removal techniques
      - Context Preservation
      - Output formatting
6. Integration and Enhancement/UI Development
      - System Integration/Component integration
      - End-to-end testing 
      - Performance Optimization
      - user interface refinement
      - interactive features
      - Visualization components
7. Testing and Documentation 
      - Comprehensive testing 
      - Unit Testing 
      - Integration testing 
      - Performance testing 
      - User acceptance testing



## Research Writing Phase/Structure 

1. Introduction
   - Problem Statement
   - Current Challenges
   - Proposed Solution

2. Related Work
    - Existing Bias Detection Methods
    - Multi-Agent Systems in NLP
    

3. Methodology
     - System Architecture
     - Agent Descriptions
     - Implementation Details

4. Experiments
    - Dataset Description
    - Evaluation Metrics
    - Results Analysis

5. Discussion
   - Comparative Analysis
   - Limitations
   - Future Work


## Folder Structure


```

project_root/
├── src/
│   ├── component/
│   │   ├── bias_analyzer_agent/
│   │   ├── fact_checker_agent/
│   │   ├── news_collector_agent/
│   │   ├── retrieverAgent/
│   │   └── UpdaterAgent/
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
│           ├── app.py            
│           ├── pages/            
│           └── components/       
├── system_evaluation/
│   ├── result/
│   ├── test_dataset/
│   ├── evaluate.py
│   ├── metrics.py
│   └── visualization.py
├── unit_tests/                     
│   ├── test_api_keys.py
│   ├── test_bias_analyzer.py
│   ├── test_fact_checking.py
│   ├── test_integration.py
│   ├── test_news_collector.py
│   └── test_retriever_updater.py
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
    └── preliminary_findings/
```

___



## Contact
**Advisor: Amir Jafari**

   Email: ajafari@gmail.com

   The George Washington University, Washington DC

   Data Science Program

   GitHub: https://github.com/amir-jafari/Capstone


