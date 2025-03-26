## Project: Group 6: Improved Multi-Agent Knowledge Sharing Systems
## Title: Improved  Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs for News Bias Detection and Fact-Checking

A multi-agent system that uses dynamic knowledge graph to detect and analyze media bias in news articles , fact-check the new topics/articles.

Proposed by Group6 Students - Initiative and Idea 

## Project Objectives:
The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased and fact-check of News topics/Articles. This project will explore the effects of shared memory on a multi-agent system and look at utilizing dynamic knowledge graphs to improve the overall efficiency of the system and accuracy of predictions and quality of  News. Specifically, this project will focus on:

Developing several agents based on customizing open-source LLMs for specific tasks, such as bias detection, Fact-checking, knowledge graph maintenance, data collection, and chat functionality.
Evaluating the effect of shared memory on a multi agent system, specifically focusing on the effect of deploying dynamic knowledge graphs compared to other methods. Evaluation metrics will focus on comparing compute resources, reducing redundancy of collected information, accuracy of bias classification and fact-checking, for quality of news.


This project implements a sophisticated multi-agent system that collaborates to collect, analyze, and fact-check news articles while maintaining a knowledge graph of verified information.

## System Architecture
 
![image](https://github.com/user-attachments/assets/019606a0-2dae-4edc-a896-ae76a23aec76

![image](https://github.com/user-attachments/assets/019606a0-2dae-4edc-a896-ae76a23aec76)

The system consists of five specialized agents that work together:

1. **News Collector Agent**: Collects news articles from NewsAPI and other sources
2. **Bias Analyzer Agent**: Analyzes news articles for potential bias and political leaning
3. **Updater Agent**: Maintains the knowledge graph with new articles and analysis
4. **Retriever Agent**: Retrieves balanced information from the knowledge graph
5. **Fact Checker Agent**: Verifies factual claims in news articles

## System Architecture Workflow/Interaction Diagram:

##  Agent Workflow Routes

# Route 1: Direct Query Processing-Factchecking 

User: User provides a specific claim or article query to Agent 5

Agent 5: Fact Checker Agent: Checks knowledge graph for existing fact checks, if needed, Performs new fact-checking analysis,  Returns verified facts to the user

# Route 2: News Collection and Bias Analysis

Agent 1: News Collector Agent: Collects political news(specifically) from NewsAPI ; Passes collected articles to Bias Analyzer

Agent 2: Bias Analyzer Agent : Analyzes bias in news articles; Verifies claims; Classifies articles as biased or unbiased; Passes analyzed articles to Updater Agent

Agent 3: Updater Agent:  Integrates analyzed news articles into knowledge graph; Stores bias analysis results

Agent 4: Retriever Agent: Retrieves balanced information from knowledge graph ; Generates summaries with bias trends and balanced perspectives: Returns comprehensive analysis to user


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
pytest unit_tests/ -v
```

Integration Tests
```bash
cd tests_int
pytest -c integration_pytest.ini 
```

### System Evaluation 

system evaluation is done on several metrics 
- fact-checking accuracy 
- Bias detection precision and recall 
- Processing efficiency 
- Knowledge graph integration effectiveness

Run the evaluation 

```bash 
python sys_evaluation/evaluate.py
```



### AWS Credentials in Educational Environment 
This system uses AWS Bedrock for lLM functionality, which requires valid AWS credentials
This AWS credentials have limited lifespans: 

1. AWS session tokens expire after several hours and need to be refreshed 
2. In the integration test phase are designed to handle credential limitations by gracefully skipping rather than failing 
3. When using the system, you may need to refresh AWS credentials periodically 

When AWS credentials expire, the system will fallback to minimal operation mode for demonstration purpose.
This is an expected limitation of AWS used for educational purposes and this does not reflect any issues with the underlying code. 

## Project  Folder Structure

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


