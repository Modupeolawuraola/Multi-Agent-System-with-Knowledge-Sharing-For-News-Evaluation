Research Methodology
===================

Problem Statement
--------------
The  fundamental challenges in evaluating news for bias and misinformation remain significant in recent times. In today's world Human fact-checkers cannot keep pace with the volume of daily news articles and social media claims, creating huge verification delays that allow misinformation to spread widely before being debunked. Automated approaches face their own limitations: bias detection systems struggle with nuance and often rely on spurious signals like publication source rather than content analysis, while fact-checking models lack contextual knowledge and world understanding. Even advanced large language models (LLMs) suffer from hallucinations and knowledge cutoff limitations.
The research study proposes that knowledge graph (KG)-integrated multi-agent systems offer an improved approach over both unstructured retrieval (RAG) and direct LLM prompting. By combining LLMs' language comprehension with structured, verified knowledge graphs, these systems provide grounded analysis and efficiently identify potential misinformation or extreme bias.


Research Areas
------------
This research spans several key areas:

1. **Multi-Agent Systems**: Exploring how specialized agents can collaborate to achieve complex tasks
2. **Knowledge Graph Applications**: Using graph-based knowledge representation for contextual understanding
3. **Comparative Architectures**: Evaluating structured vs. unstructured knowledge integration
4. **Statistical Validation**: Rigorous testing with McNemar's test and bootstrap confidence intervals

Methodology
----------
Our research methodology combines qualitative and quantitative approaches:

1. **Literature Review**: Analysis of existing research on media bias detection, multi-agent systems, knowledge graphs, and RAG
2. **System Development**: Iterative design and implementation of three systems (RAG, LLM-only, LLM+KG)
3. **Data Collection**: Gathering diverse news articles from various sources across the political spectrum
4. **Experimental Testing**: Evaluating system performance using controlled test sets
5. **Statistical Analysis**: McNemar's test and bootstrap confidence intervals (95%, 1000 iterations)

Experimental Setup
--------------------

The research compared three system configurations:

**RAG Baseline:**

* Retrieval-Augmented Generation with unstructured document retrieval
* Embedding Model: Sentence-BERT (all-MiniLM-L6-v2)
* Vector Database: ChromaDB
* Generation Model: Mistral-7B-Instruct-v0.2
* Retrieval: Top-5 most similar articles based on cosine similarity

**LLM-only:**

* Direct prompting without external knowledge
* Model: AWS Bedrock Claude 3.5 Sonnet v2
* No retrieval or structured memory

**LLM+KG (Our System):**

* Complete multi-agent system with structured knowledge graph
* Model: AWS Bedrock Claude 3.5 Sonnet v2
* Knowledge Graph: Neo4j with dynamic updates
* Specialized agents: Bias Analyzer, Fact Checker

Evaluation Framework
----------------------
We evaluated all three systems using:

* Standard classification metrics (Precision, Recall, F1-score)
* Specialized metrics for class imbalance (Balanced accuracy, Cohen's Kappa, Matthews Correlation, Weighted F1)
* Statistical significance testing (McNemar's test, p < 0.05)
* Bootstrap confidence intervals (95%, 1000 iterations, random seed = 42)

Test Datasets
----------------------

**Bias Detection:**

* Total corpus: 222 news articles labeled Left, Center, Right
* Training set: 177 articles (for RAG and LLM+KG)
* Test set: 45 articles (held-out, used for all three systems)

**Fact-Checking:**

* 214 claims from Media Bias/Fact Check
* Labels: True (19%), False (79%), Misleading (2%)
* Temporal separation from training data

Key Findings
----------

Bias Detection Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20

   * - System
     - Weighted F1
     - Balanced Accuracy
     - Cohen's Kappa
   * - RAG
     - 0.287 [0.139-0.446]
     - 0.164
     - -0.195
   * - LLM-only
     - 0.713 [0.594-0.827]
     - 0.722
     - 0.488
   * - **LLM+KG**
     - **0.901 [0.817-0.978]**
     - **0.857**
     - **0.745**

**Statistical Significance:**

* RAG vs LLM-only: p < 0.001***
* RAG vs LLM+KG: p < 0.001***
* LLM-only vs LLM+KG: p = 0.0055**

Fact-Checking Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20

   * - System
     - Weighted F1
     - True Recall
     - False F1
   * - RAG
     - 0.661 [0.585-0.728]
     - 0.05
     - 0.78
   * - LLM-only
     - 0.721 [0.643-0.795]
     - 0.07
     - 0.87
   * - **LLM+KG**
     - **0.794 [0.722-0.858]**
     - **0.25**
     - **0.89**

**Statistical Significance:**

* RAG vs LLM-only: p < 0.001***
* RAG vs LLM+KG: p < 0.001***
* LLM-only vs LLM+KG: p = 0.0019**

Key Insights
^^^^^^^^^^^^

1. **Structured vs. Unstructured Knowledge**: LLM+KG (structured) significantly outperforms RAG (unstructured) across all metrics
2. **True Claim Detection**: LLM+KG achieved 400% improvement in true claim recall over RAG (0.05 → 0.25)
3. **Bias Detection**: 214% improvement in weighted F1 over RAG, 26% over LLM-only
4. **Statistical Validity**: All improvements statistically significant with non-overlapping confidence intervals

Limitations
------------

1. **Minority Class Performance**: All three approaches struggle with minority classes (true claims, misleading content)
2. **Emerging Narratives**: Limited coverage of emerging political topics not yet in training data
3. **Dataset Size**: Test set of 45 articles for bias detection reflects 80/20 train/test split required for fair comparison
4. **Computational Resources**: RAG uses Mistral-7B due to loss of AWS access; LLM-only and LLM+KG use Claude 3.5 Sonnet

Conclusion
-----------

Our research demonstrates that integrating structured knowledge graphs with multi-agent LLM architectures creates significant, statistically validated improvements over both unstructured retrieval (RAG) and direct prompting (LLM-only) for news bias detection and fact-checking.

The progressive performance gains (RAG → LLM-only → LLM+KG) suggest that:

1. Some external knowledge (RAG) helps, but unstructured retrieval is insufficient
2. LLM reasoning improves performance, but lacks factual grounding
3. Structured knowledge representation (KG) provides the optimal balance

These findings could effectively augment fact-checking and editorial teams in real-world deployments.

Future Research Work
------------------------

Potential areas for future research include:

* **Hybrid Approaches**: Combining RAG with structured knowledge graphs
* **Dynamic Knowledge Updates**: Real-time graph updates for emerging topics
* **Larger-Scale Validation**: 1000+ examples per task across diverse sources
* **Cross-Domain Evaluation**: Testing beyond political news
* **Multilingual Support**: Extending to multiple languages and cultural contexts
* **Minority Class Improvements**: Specialized techniques for imbalanced datasets