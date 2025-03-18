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


## Agent Architecture Interaction Diagram:

Anticipated Multi-Agent System Workflow:

Route 1-  User provides  a topic or article query to the system→ **Agent5** Agent 5 checks for existing knowledge in the knowledge graph, fact-check it 
Return the Fact to the User.

Route 2- **Agent1-New Collector Agent** Collect polictical news from newsAPI then pass it to the **Agent 2** bias detector/analyzer to analyse

**Agent2- Bias Analyzer/Detector Agent** analyze the bias in the news article , check verify the claims if its biased or unbiased  pass it to agent 4- Agent Updater

**Agent3- Updater Agent ** integrates verified/analysed  news articles / data into knowledge graph.

**Agent4- Retriever Agent **collecte/ generates an unbiased news articles from the knowledgeGraph/ Memory.

 From **Agent 4- Retriever Agent ** returns a response and summary , bias trends and balanced perspectives to User.


```bash
Diagram
```
## Knowledge Graph

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
    - News Summarization Techniques

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

├── src
│   ├── component
│   
├── demo  |
│   └── fig
├── full_report
│   ├── Latex_report
│   │   └── fig
│   ├── Markdown_Report
│   └── Word_Report
├── presentation
└── research_paper
    ├── Latex
    │   └── Fig
    └── Word
```

___



## Contact
**Advisor: Amir Jafari**

   Email: ajafari@gmail.com

   The George Washington University, Washington DC

   Data Science Program

   GitHub: https://github.com/amir-jafari/Capstone


