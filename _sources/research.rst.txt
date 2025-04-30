Research Methodology
===================

Problem Statement
--------------
The  fundamental challenges in evaluating news for bias and misinformation. In today's world Human fact-checkers cannot keep pace with the volume of daily news articles and social media claims, creating huge verification delays that allow misinformation to spread widely before being debunked. Automated approaches face their own limitations: bias detection systems struggle with nuance and often rely on spurious signals like publication source rather than content analysis, while fact-checking models lack contextual knowledge and world understanding. Even advanced large language models (LLMs) suffer from hallucinations and knowledge cutoff limitations.
The research study proposes that knowledge graph (KG)-integrated multi-agent systems offer an improved approach over traditional or LLM-only methods. By combining LLMs' language comprehension and reasoning abilities with KGs' verified, up-to-date information, these systems can provide grounded analysis and efficiently flag potential misinformation or extreme bias for human review.


Research Areas
------------
This research spans several key areas:

1. **Multi-Agent Systems**: Exploring how specialized agents can collaborate to achieve complex tasks
2. **Knowledge Graph Applications**: Using graph-based knowledge representation for contextual understanding
3. **Large Language Model Customization**: Fine-tuning LLMs for specific bias detection and fact-checking tasks

Methodology
----------
Our research methodology combines qualitative and quantitative approaches:

1. **Literature Review**: Analysis of existing research on media bias detection, multi-agent systems, and knowledge graphs
2. **System Development**: Iterative design and implementation of the multi-agent system
3. **Data Collection**: Gathering diverse news articles from various sources across the political spectrum
4. **Experimental Testing**: Evaluating system performance using controlled inputs and comparing against human assessments
5. **Comparative Analysis**: Using LLM Performance Benchmarking against  new system benchmarking , LLM +KG

Results Analysis
--------------

Experimental Setup
--------------------

The research compared two system configurations:

LLM-only: A baseline system using AWS Bedrock LLM -Claude 3.5 Sonnet v2 with direct prompting
LLM+KG: Our complete multi-agent system integrating knowledge graph with the same LLM in AWS Bedrock LLM

Evaluation Framework
----------------------
We evaluated our system using standard classification metrics (Precision, Recall, F1-score, Accuracy) alongside specialized metrics tailored to handle class imbalance in our datasets (Balanced accuracy, Cohen's Kappa, Matthews Correlation Coefficient, Weighted F1).

Test datasets
----------------------

Test datasets included:
Fact-checking dataset: 210 claims (19% True, 81% False)
Bias detection dataset: 222 articles labeled as Left, Center, or Right


System Testing and Evaluation
----------------------------

This research employed a comprehensive testing approach combining isolated component evaluation(unit-testing) and end-to-end system testing(integration test).
We developed a Streamlit user interface allowing natural language interaction with the system.



Key Findings
----------
Fact-Checking Performance

LLM+KG showed significant improvement in detecting true claims (recall increased from 0.07 to 0.25)
Overall micro-average F1 score improved from 0.77 to 0.82
Macro-average F1 score increased from 0.49 to 0.63

Bias Detection Performance

LLM+KG achieved balanced accuracy of 0.823 (vs. 0.735 for LLM-only)
Cohen's kappa improved significantly from 0.488 to 0.745
Matthews correlation coefficient increased from 0.574 to 0.759


Limitations
------------
The system occasionally struggles with emerging political narratives not yet well represented in the knowledge graph.
Limited articles on specific topics may have outsized influence, potentially presenting skewed rather than balanced contextual information.


Conclusion
-----------

Our research demonstrates that integrating knowledge graphs with multi-agent LLM architectures creates significant improvements in news bias detection and fact-checking capabilities.
We observed performance gains across all metrics suggest this approach could effectively augment fact-checking and editorial teams.


Future Research Work
------------------------
Potential areas for future research include:

- Exploring approaches to improve handling of emerging topics
- Extending the system to handle more languages and cultural contexts
- Implementing more sophisticated bias detection mechanisms
- Developing more advanced knowledge sharing architectures among agents

