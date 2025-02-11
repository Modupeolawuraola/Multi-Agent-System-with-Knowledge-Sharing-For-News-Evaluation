import json
import os
import shutil


def save_to_json(data, output_file_path):
    with open(output_file_path, 'w') as output_file:
        json.dump(data, output_file, indent=2)


data_to_save = \
    {
        # -----------------------------------------------------------------------------------------------------------------------
        "Version":
            """7""",
        # -----------------------------------------------------------------------------------------------------------------------
        "Year":
            """2025""",
        # -----------------------------------------------------------------------------------------------------------------------
        "Semester":
            """Spring""",
        # -----------------------------------------------------------------------------------------------------------------------
        "project_name":
            """Improved Multi-Agent Knowledge Sharing Systems""",
        # -----------------------------------------------------------------------------------------------------------------------
        "Objective":
            """ 
        The goal of this project is to design, develop, and validate a multi-agent chatbot that is capable of detecting media bias in news articles and providing unbiased summaries of the topic. 
        This project will explore the effects of shared memory on a multi-agent system and look at utilizing dynamic knowledge graphs to improve the overall efficiency of the system and accuracy of predictions and quality of summarizations. 
        Specifically, this project will focus on:
        Developing several agents based on customizing open-source LLMs for specific tasks, 
        such as bias detection, summarization, knowledge graph maintenance, data collection, and chat functionality.
        Evaluating the effect of shared memory on a multi agent system, specifically focusing on the effect of deploying dynamic knowledge graphs compared to other methods. 
        Evaluation metrics will focus on comparing compute resources, reducing redundancy of collected information, accuracy of bias classification, and quality of news summarization.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Dataset":
            """
            The dataset for fine-tuning and customization is still TBD. However, data will likely consist of relevant open-source news,
         datasets, and domain-specific content to build the required context for news perspectives.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Rationale":
            """Generative AI (genAI) technology offers a novel approach to supporting News Bias given that routinely the diversity of team member participants is limited. By using LLM-based chatbots for this News industry. In this project, we will explore how an AI-driven team collaboration can  act as an Multi-agent system intervention.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Approach":
            """
            The project will proceed in several phases:
            Requirement Analysis: Collaborate with lead researchers to define key components of News knowledge sharing experiences and specify chatbot performance requirements.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Timeline":
            """
            This is a rough timeline for the project:
         **Weeks 1-2**: Familiarization with project requirements, intellectual humility constructs, and open-source tools.
         **Weeks 3-8**: Design, develop, and build a working prototype.
         **Weeks 9-12**: Iterative testing and improvement of chatbot performance, incorporating feedback from simulated interactions.
         **Weeks 13-16**: Multi-agent testing and usability evaluation.
         **Weeks 17-18**: Final reporting, documentation, and presentation of outcomes.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Expected Number Students":
            """
            This project is suitable for a team of 2-3 students, given the scope and need for interdisciplinary collaboration.
            """,
        # -----------------------------------------------------------------------------------------------------------------------
        "Possible Issues":
            """
            Potential challenges for this project include:
             **Limited Training Data**: Finding appropriate datasets for Knowledge Graph or fine-tuning the LLM may be a limiting factor.
             **Complexity of Interdisciplinary Teams**: Designing prompts and interactions to genuinely foster  collaborations of diverse teams, requiring careful iteration and feedback.
             **Interdisciplinary Collaboration**: This project spans multiple disciplines news article (e.g.,  Health news, Politics News, Education News, Technology News), 
             requiring effective collaboration and understanding across fields.
            """,

        # -----------------------------------------------------------------------------------------------------------------------
        "Proposed by": "Group 6-Christopher Washer , Modupeola Fagbenro, Pavani",
        "Proposed by email": "cwasher@gwu.edu",
        "instructor": "Amir Jafari",
        "instructor_email": "ajafari@gmail.com",
        "github_repo": "https://github.com/amir-jafari/Capstone",
        # -----------------------------------------------------------------------------------------------------------------------
    }
os.makedirs(
    os.getcwd() + os.sep + f'Arxiv{os.sep}Proposals{os.sep}{data_to_save["Year"]}{os.sep}{data_to_save["Semester"]}{os.sep}{data_to_save["Version"]}',
    exist_ok=True)
output_file_path = os.getcwd() + os.sep + f'Arxiv{os.sep}Proposals{os.sep}{data_to_save["Year"]}{os.sep}{data_to_save["Semester"]}{os.sep}{data_to_save["Version"]}{os.sep}'
save_to_json(data_to_save, output_file_path + "input.json")
shutil.copy('json_gen.py', output_file_path)
print(f"Data saved to {output_file_path}")
