## Project: Group 6: Improved Multi-Agent Knowledge Sharing Systems
### Title: Improved  Multi-Agent Knowledge Sharing System using Dynamic Knowledge Graphs for News Bias Detection and Fact-Checking

**Status:** ✅ Published in Neural Computing and Applications (March, 2026)

**Read the paper:** https://link.springer.com/article/10.1007/s00521-026-11944-0

**Citation:**
Fagbenro, M., Washer, C., Chella, P., & Jafari, A. (2026). 

*Neural Computing and Applications*.  Published [March, 2026]

## Project Overview:

The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased and fact-check of News topics/Articles.
This project explores how integrating structured knowledge graphs as shared memory enhances multi-agent systems for news evaluation tasks. We compare three distinct approaches:

1. **RAG Baseline**: Retrieval-Augmented Generation using unstructured document retrieval
2. **LLM-Only**: Direct prompting without external knowledge
3. **LLM+KG** (Our System): Multi-agent system with structured knowledge graph integration

### Key Findings

Our experiments demonstrate that structured knowledge graph integration significantly outperforms both unstructured retrieval (RAG) and direct LLM prompting:

**Bias Detection (Weighted F1):**
- RAG: 0.287
- LLM-only: 0.713
- **LLM+KG: 0.901**  (214% improvement over RAG, 26% over LLM-only)

**Fact-Checking (Weighted F1):**
- RAG: 0.661
- LLM-only: 0.721
- **LLM+KG: 0.794**  (20% improvement over RAG, 10% over LLM-only)

All improvements are statistically significant (p < 0.01) based on McNemar's test with bootstrap confidence intervals.



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

### Baseline Systems (For Comparison)

**RAG Baseline**:
- Embedding Model: Sentence-BERT (all-MiniLM-L6-v2)
- Vector Database: ChromaDB
- Generation Model: Mistral-7B-Instruct-v0.2
- Retrieval: Top-5 most similar articles based on cosine similarity

**LLM-Only Baseline**:
- Direct prompting with Claude 3.5 Sonnet
- No external knowledge retrieval or structured memory

## System Architecture Workflow/Interaction Diagram:
The system implement a flexible, knowledge -graph -centered architecture with specialized agents that operate independently but share information through a centralized knowledge repository.  

# Processing Route:
The LLM+KG system supports three main processing routes:

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
<img width="672" alt="Screenshot 2025-04-29 at 1 10 56 PM" src="https://github.com/user-attachments/assets/3b927a22-cd86-4f02-ab0d-5b7eea1a2148" />


## Tech Stack:

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Pytorch-%23FF6F00.svg?style=for-the-badge&logo=Pytorch&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-3670A0?style=for-the-badge&logo=Neo4j&logoColor=ffdd54)
![React](https://img.shields.io/badge/Docker-%2320232a.svg?style=for-the-badge&logo=Docker&logoColor=%2361DAFB)
![Pytorch](https://img.shields.io/badge/Aws-%23FF6F00.svg?style=for-the-badge&logo=Aws&logoColor=white)

## Technologies Used
**LLM+KG System**:
- **Large Language Models**: Claude 3 via AWS Bedrock
- **Knowledge Graph**: Neo4j
- **Backend**: Python
- **API Integration**: NewsAPI for article collection
- **Testing Framework**: Pytest

**RAG Baseline**:
- Generation Model: Mistral-7B-Instruct-v0.2
- Vector Database: ChromaDB
- Embedding Model: Sentence-Transformers (all-MiniLM-L6-v2)

**Shared Components**:
- API Integration: NewsAPI for article collection
- Testing Framework: Pytest

---
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

**LLM+KG System** (Main):
```bash
python main.py
```
**RAG Baseline**:
```bash
python rag_baseline/run_rag.py
```

**LLM-Only Baseline**:
```bash
python llm_only_baseline/run_llm_only.py
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

## System Evaluation 
### Evaluation Setup

Our evaluation compared three approaches on the same test datasets:
- **Bias Detection**: 45 news articles (held-out test set from 222-article corpus)
- **Fact-Checking**: 214 claims from Media Bias/Fact Check

### Metrics

**Bias Detection**:
- Balanced Accuracy
- Cohen's Kappa
- Matthews Correlation Coefficient
- Weighted F1

**Fact-Checking**:
- Precision, Recall, F1 (per class)
- Weighted F1
- Macro F1

**Statistical Testing**:
- McNemar's test for pairwise comparisons
- Bootstrap confidence intervals (95%, 1000 iterations)
- Random seed = 42 for reproducibility

### Running Evaluations

**Bias Detection**:
```bash
# LLM+KG
python sys_evaluation/evaluate_bias.py

# RAG Baseline
python sys_evaluation/evaluate_bias_rag.py

 LLM-Only
python sys_evaluation/evaluate_bias_llm_only.py
```

**Fact-Checking**:
```bash
# LLM+KG
python sys_evaluation/evaluate_factcheck.py

# RAG Baseline
python sys_evaluation/evaluate_factcheck_rag.py

# LLM-Only
python sys_evaluation/evaluate_factcheck_llm_only.py
```

**Statistical Analysis**:
```bash
python sys_evaluation/statistical_tests.py
```
---

## Key Results

### Bias Detection Performance

| System | Weighted F1 | Balanced Accuracy | Cohen's Kappa |
|--------|-------------|-------------------|---------------|
| RAG | 0.287 [0.139-0.446] | 0.164 | -0.195 |
| LLM-only | 0.713 [0.594-0.827] | 0.722 | 0.488 |
| **LLM+KG** | **0.901 [0.817-0.978]** | **0.857** | **0.745** |

**Statistical Significance**:
- RAG vs LLM-only: p < 0.001***
- RAG vs LLM+KG: p < 0.001***
- LLM-only vs LLM+KG: p = 0.0055**

### Fact-Checking Performance

| System | Weighted F1 | True Recall | False F1 |
|--------|-------------|-------------|----------|
| RAG | 0.661 [0.585-0.728] | 0.05 | 0.78 |
| LLM-only | 0.721 [0.643-0.795] | 0.07 | 0.87 |
| **LLM+KG** | **0.794 [0.722-0.858]** | **0.25** | **0.89** |

**Statistical Significance**:
- RAG vs LLM-only: p < 0.001***
- RAG vs LLM+KG: p < 0.001***
- LLM-only vs LLM+KG: p = 0.0019**

---


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
### Data Availability

- News articles collected via NewsAPI (cannot be redistributed due to API terms)
- Bias ratings from AllSides (publicly available)
- Fact-checking claims from Media Bias/Fact Check (publicly available)
- Labeled datasets and evaluation results available in `sys_evaluation/results/`
---

## Project  Folder Structure

```


project_root/
├── src/
│   ├── component/
│   │   ├── bias_analyzer_agent/
|   |   |--- rag_baseline/
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

## Citation

If you use this work, please cite:
```bibtex
@article{fagbenro2025multiagent,
  title={Improved Multi-Agent Knowledge Sharing System using Knowledge Graphs for News Bias Detection and Fact-Checking},
  author={Fagbenro, Modupeola and Washer, Christopher and Chella, Pavani and Jafari, Amir},
  journal={Neural Computing and Applications},
  year={2025},
  note={Under Review}
}
```
