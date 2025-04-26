## Project: Group 6: Improved Multi-Agent Knowledge Sharing Systems
## Title: Improved  Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs for News Bias Detection and Fact-Checking

A multi-agent system that uses dynamic knowledge graph to detect and analyze media bias in news articles , fact-check the news topics/articles.

Proposed by Group6 Students  

## Project Objectives:
The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased and fact-check of News topics/Articles. This project will explore the effects of shared memory on a multi-agent system and look at utilizing dynamic knowledge graphs to improve the overall efficiency of the system and accuracy of predictions and quality of  News. Specifically, this project will focus on:

1. Developing specialized multi-agents system based on customizing open-source LLMs for specific tasks, such as bias detection, Fact-checking, knowledge graph maintenance, data collection from news open source API, and chatbot functionality.

2. Evaluating the effect of shared memory on a multi agent system, specifically focusing on the effect of deploying dynamic knowledge graphs compared to other methods. Evaluation metrics will focus on system performance improvement, reducing redundancy of collected information, accuracy of bias classification and fact-checking, for quality of news.



## System Architecture

<img width="929" alt="Screenshot 2025-04-21 at 7 33 52 PM" src="https://github.com/user-attachments/assets/82179473-458b-4cb4-ac3d-64779b81b3fa" />




The system consists of several components that work together:

1. **Knowledge Graph** : A Neo4j-based dynamic knowledge repository that stores news articles and entity relationships
2. **Specialized Agents** :
 **Bias Analyzer Agent** : Analyzes  political news articles bias and leaning
 **Fact Checker Agent** : Verifies factual claims against knowledge graph context and internal knowledge
3. **Agent Manager** :Orchestrates workflow between agents
Routes user requests to appropriate processing paths
Returns consolidated results to the user interface
4. **Integration Framework**:

**GraphState Schema**: Standardized data structure for agent communication

**Streamlit UI**: User-friendly interface for interacting with the multi-agent system. This streamlined architecture enables efficient information sharing through the knowledge graph, allowing agents to leverage collaborative intelligence also maintaining specialized expertise in their respective domains. 


## System Architecture Workflow/Interaction Diagram:
The system implement a flexible, knowledge -graph -centered architecture with specialized agents that operate independently but share information through a centralized knowledge repository.  

# Processing Route: 
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

Modular Design: Agents function independently and can be developed/tested separately
Flexible Routing: Multiple entry points based on user needs
Shared Knowledge: Central knowledge graph eliminates redundant processing
Improved Performance: Knowledge graph integration enhances accuracy compared to LLM-only approaches



System Capabilities
1. Fact-checking of direct user queries
2. Automated news collection and bias analysis
3. Persistent storage of analyzed articles in knowledge graph
4. Retrieval of balanced news perspectives

## Knowledge Graph WorkFlow
Our system employs a dynamic knowledge graph for information storage and retrieval.


Structure:
![project_KG_schema](https://github.com/user-attachments/assets/3a0c1cde-cd08-42c9-bdff-58ccf2b44d90)

## Tech Stack:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Pytorch-%23FF6F00.svg?style=for-the-badge&logo=Pytorch&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-3670A0?style=for-the-badge&logo=Neo4j&logoColor=ffdd54)
![React](https://img.shields.io/badge/Docker-%2320232a.svg?style=for-the-badge&logo=Docker&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Aws-%23FF6F00.svg?style=for-the-badge&logo=Aws&logoColor=white)

## Technologies Used

- **Large Language Models**: Claude 3 via AWS Bedrock
- **Knowledge Graph**: Neo4j
- **Backend**: Python
- **API Integration**: NewsAPI for article collection
- **Testing Framework**: Pytest


## Getting started:



### Pre-requisites  

- Python 3.10+
- AWS account with Bedrock access
- Neo4j database
- NewsAPI key

### Installation

1. Clone the repository 
```bash
git clone https://github.com/Modupeolawuraola/Multi-Agent-System-with-Knowledge-Sharing-For-News-Evaluation.git
cd Multi-Agent-System-with-Knowledge-Sharing-For-News-Evaluation
```

### Install dependencies 

```bash
pip install -r requirement.txt
```

### Instruction on Environment variable Setup 

Setup environment variables create .env file in the src directory with the following variables
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_SESSION_TOKEN=your_aws_session_token
AWS_REGION=us-east-1
NEWS_API_KEY=your_news_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

### Running the system 

```bash
python main.py
```

### Testing 
Unit Tests 

```bash
pytest unit_tests_v2/ -v
```

Integration Tests
```bash
pytest tests_int_v2/test_integration_real_aws.py
  
```

### System Evaluation 

**System Evaluation**
Evaluation metrics includes  measuring:

1. Accuracy of bias classification (balanced accuracy, Cohen's kappa)

2. Fact-checking performance (precision, recall, F1 scores)

3. Overall system quality (weighted F1, Matthews correlation)

The system evaluation focused on comparing performance between LLM-only and LLM+KG configurations across several metrics:

1. **Fact-Checking Performance**

- Precision: LLM-Only  vs. LLM+KG 

- Recall for True Claims: LLM-Only  vs. LLM+KG 

- Overall F1-Score: LLM-Only vs. LLM+KG 

2 **Bias Detection Performance**

- Balanced Accuracy: LLM-Only vs. LLM+KG

- Cohen's Kappa: LLM-Only  vs. LLM+KG 

- Matthews Correlation: LLM-Only vs. LLM+KG 

- Weighted F1: LLM-Only  vs. LLM+KG 

3 **Knowledge Graph Integration Effectiveness**

- Most significant improvements in inter-rater reliability metrics (Cohen's Kappa: 53% increase)

- Substantial improvement in true claim detection (257% increase in recall)

- Enhanced contextual understanding for political content analysis


Run the evaluation 

```bash 
python sys_evaluation/evaluate_bias.py
```



### AWS Credentials in Educational Environment 
This system uses AWS Bedrock for LLM functionality, which requires valid AWS credentials
This AWS credentials have limited lifespans: 

1. AWS session tokens expire after several hours and need to be refreshed 
2. In the integration test phase are designed to handle credential limitations by gracefully skipping rather than failing 
3. When using the system, you may need to refresh AWS credentials periodically 

When AWS credentials expire, the system will fallback to minimal operation mode for demonstration purpose.
This is an expected limitation of AWS used for educational purposes and this does not reflect any issues with the underlying code. 

### UI interface 


Our system provides an intuitive chat interface built with Streamlit:


<img width="885" alt="ui1" src="https://github.com/user-attachments/assets/1e9fec3f-0db7-4253-96f5-1c94618ebe78" />

<img width="898" alt="ui2" src="https://github.com/user-attachments/assets/9b0d55d3-153b-4ca3-8840-fadaf032127b" />

### Visualization-slideshow 

```markdown

![Project Visualization Summary](visualization_slideshow/visualization_slideshow.gif)

```


## Project  Folder Structure

```


project_root/
├── src/
│   ├── component/
│   │   ├── bias_analyzer_agent/
│   │   ├── fact_checker_agent/
│   │   ├── KG Builder/
│   │   
│   │___|___agent_manager/ manager.py & transistion.py
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
│           ├── chatbot_ui.py            
│            
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
│   
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
    └── preliminary_findings/
```

___



## Contributor 

**Group 6- Students:**

   -Pavani chella (@pvani)

   -Modupeola Fagbenro (@Modupeolawuraola)

   -Chris Washer (@chrisjwasher)




## Acknowledgements 

## Contact
**Advisor: Amir Jafari**

   Email: ajafari@gmail.com

   The George Washington University, Washington DC

   Data Science Program

   GitHub: https://github.com/amir-jafari/Capstone


