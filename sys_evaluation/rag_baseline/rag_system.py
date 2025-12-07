"""
Developing RAG baseline for News Bias Detection and Fact checking

Uses: Sentence Transformers + ChromaDB + Mistral-7B
"""

from sentence_transformers import SentenceTransformer
from transformers import pipeline
import chromadb
import json
import logging


class RAGBaseline:
    """
    Simple RAG system for comparison with LLM+KG approach

    Architecture:
    1. Embed articles with Sentence Transformers
    2. Store in ChromaDB (local vector database)
    3. Retrieve top-k similar articles
    4. Pass context to Mistral-7B for classification
    """

    def __init__(self, model_name='mistralai/Mistral-7B-Instruct-v0.2'):
        logging.info("RAG baseline initialization")

        # 1. EMBEDDINGS (retrieval component)
        logging.info("Loading Embedding model.....")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # 2. VECTOR STORE (storage component)
        logging.info("Initializing Chromadb vector store.....")
        self.client = chromadb.PersistentClient(path="./rag_db")

        # Create collections for bias and fact checking
        try:
            self.bias_collection = self.client.get_collection("bias_articles")
        except:
            self.bias_collection = self.client.create_collection("bias_articles")

        try:
            self.fact_collection = self.client.get_collection("fact_articles")
        except:
            self.fact_collection = self.client.create_collection("fact_articles")

        # 3. LLM (generation component)
        logging.info(f"Loading LLM Model: {model_name}.....")
        self.llm = pipeline(
            "text-generation",
            model=model_name,
            max_new_tokens=512,
            temperature=0.2,
            device=-1,  # CPU
            torch_dtype="auto"
        )
        logging.info("RAG baseline initialization successful.....")

    def add_articles_for_bias(self, articles):
        """
        Add articles to vector database for bias detection

        Args:
            articles (list): List of article dicts with 'title', 'content', 'source', 'ground_truth_bias'
        """
        logging.info(f"Adding {len(articles)} articles to bias collection......")

        for i, article in enumerate(articles):
            text = f"{article['title']} {article['content']}"

            self.bias_collection.add(
                documents=[text],
                metadatas=[{
                    "source": article.get('source', 'unknown'),
                    "bias": article.get('ground_truth_bias', 'unknown')
                }],
                ids=[f"bias_article_{i}"]
            )
            if i % 20 == 0:
                logging.info(f"Added {i+1}/{len(articles)} articles")

    def add_articles_for_factcheck(self, articles):
        """
        Add articles to vector database for fact checking

        Args:
            articles (list): List of article dicts with 'title', 'content'
        """
        logging.info(f"Adding {len(articles)} articles to fact checking collection......")

        for i, article in enumerate(articles):
            text = f"{article['title']} {article['content']}"

            self.fact_collection.add(
                documents=[text],
                metadatas=[{
                    "source": article.get('source', 'unknown')
                }],
                ids=[f"fact_article_{i}"]
            )
            if i % 20 == 0:
                logging.info(f"Added {i+1}/{len(articles)} articles")

    def classify_bias(self, article, n_results=5):
        """
        Classify political bias using RAG

        Args:
            article: Dict with 'title' and 'content'
            n_results: Number of similar articles to retrieve

        Returns:
            Dict with 'bias' and 'reasoning'
        """
        # 1. Create query text
        query_text = f"{article['title']} {article['content']}"

        # 2. Retrieve similar articles
        results = self.bias_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        # 3. Build context from retrieved articles
        context_parts = []
        for i in range(len(results['documents'][0])):
            source = results['metadatas'][0][i]['source']
            bias = results['metadatas'][0][i]['bias']
            snippet = results['documents'][0][i][:300]  # First 300 chars

            context_parts.append(
                f"Article {i+1} from {source} (known bias: {bias}):\n{snippet}"
            )
        context = "\n\n".join(context_parts)

        # 4. Create prompt for LLM
        json_format = '{"bias": "left|center|right", "reasoning": "brief explanation"}'

        prompt = f"""[INST]You are a political bias classifier. Based on similar articles and their known biases, classify the target article's political bias.

Retrieved Context:
{context}

Target Article:
Title: {article['title']}
Content: {article['content'][:800]}

Task: Classify the political bias as exactly one of: left, center, or right

Respond ONLY with valid JSON in this exact format:
{json_format}
[/INST]"""

        # 5. Generate classification
        response = self.llm(prompt, max_new_tokens=256)[0]['generated_text']

        # 6. Extract JSON from response
        try:
            if '[/INST]' in response:
                response = response.split('[/INST]')[-1].strip()

                #find first complete JSON object
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)

               #Validate and normalize bias
                bias = result.get('bias', '').lower().strip()
                if bias not in ['left', 'center', 'right']:
                    logging.warning(f"Invalid bias '{bias}', defaulting to 'unknown'")
                    bias = 'unknown'

                return {'bias': bias, 'reasoning': result.get('reasoning', '')}
            else:
                logging.error(f"No JSON found in response: {response[:200]}")
                return {"bias": "unknown", "reasoning": "Failed to parse response"}
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}. Response: {response[:200]}")
            return {"bias": "unknown", "reasoning": f"JSON parse error: {str(e)}"}
        except Exception as e:
            logging.error(f"Error parsing LLM response: {e}")
            return {"bias": "unknown", "reasoning": str(e)}

    def check_fact(self, claim, n_results=5):
        """
        Verify a factual claim using RAG

        Args:
            claim: String containing the claim to verify
            n_results: Number of relevant articles to retrieve

        Returns:
            Dict with 'verdict' and 'reasoning'
        """
        # 1. Retrieve relevant articles
        results = self.fact_collection.query(
            query_texts=[claim],
            n_results=n_results
        )

        # 2. Build context
        context = "\n\n".join([
            f"Article {i+1}: {doc[:400]}"
            for i, doc in enumerate(results['documents'][0])
        ])

        # 3. Create prompt
        json_format = '{"verdict": "true|false", "reasoning": "brief explanation"}'

        prompt = f"""[INST]You are a fact-checker. Based on news articles, verify if a claim is true or false.

Context from News Articles:
{context}

Claim to Verify: {claim}

Task: Classify as exactly: true or false

Respond ONLY with valid JSON in this exact format:
{json_format}
[/INST]"""

        # 4. Generate verdict
        response = self.llm(prompt, max_new_tokens=256)[0]['generated_text']

        # 5. Extract JSON - IMPROVED VERSION
        try:
            # Remove the prompt from response
            if '[/INST]' in response:
                response = response.split('[/INST]')[-1].strip()

            # Find FIRST complete JSON object
            json_start = response.find('{')
            json_end = response.find('}', json_start) + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)

                # Normalize verdict
                verdict = result.get('verdict', '').lower().strip()
                if verdict not in ['true', 'false']:
                    logging.warning(f"Invalid verdict '{verdict}', defaulting to 'unknown'")
                    verdict = "unknown"

                return {"verdict": verdict, "reasoning": result.get('reasoning', '')}
            else:
                logging.error(f"No JSON found in response: {response[:200]}")
                return {"verdict": "unknown", "reasoning": "Failed to parse response"}

        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}. Response: {response[:200]}")
            return {"verdict": "unknown", "reasoning": f"JSON parse error: {str(e)}"}
        except Exception as e:
            logging.error(f"Error parsing LLM response: {e}")
            return {"verdict": "unknown", "reasoning": str(e)}