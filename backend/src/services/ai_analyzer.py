from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain import PromptTemplate, LLMChain
from langchain.llms import HuggingFacePipeline
from typing import Dict, List
import torch
import json
import boto3
from datetime import datetime
from typing import Dict, List, Optional
import uuid  # For generating session IDs

class UserResponseManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('web-analyses-responses')

    def save_user_responses(
        self, 
        url: str, 
        questions: List[Dict], 
        answers: List[str],
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Save user's responses to questions
        Returns the session_id for future reference
        """
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        item = {
            'session_id': session_id,
            'timestamp': datetime.now(datetime.timezone.utc).isoformat(),
            'url': url,
            'responses': [
                {
                    'question': q['question'],
                    'options': q['options'],
                    'selected_answer': a
                } for q, a in zip(questions, answers)
            ]
        }
        
        self.table.put_item(Item=item)
        return session_id

    def get_user_responses(self, session_id: str) -> Optional[Dict]:
        """
        Get responses for a specific session
        """
        response = self.table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={
                ':sid': session_id
            }
        )
        
        items = response.get('Items', [])
        return items[0] if items else None

class AIAnalyzer:
    def __init__(self):
        # Check for GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Initialize model and tokenizer
        model_name = "distilgpt2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        
        # Initialize pipeline with GPU support
        base_pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
            framework="pt",
            max_new_tokens=500,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Create Langchain pipeline
        self.llm = HuggingFacePipeline(pipeline=base_pipeline)

    # Create a prompt template for generating a question    
    def create_questions_prompt(self):
        template = """Analyze the following website content and create a single multiple-choice question to identify the visitor's intent.

        Website Content:
        Title: {title}
        Description: {meta_description}
        Main Content: {main_content}
        Headings: {headings}

        Based on the main categories or themes found in the content, generate:
        1. A question about what the visitor is looking for
        2. Four multiple choice options (A through D) that cover the main categories found in the content

        Return the response in the following JSON format:
        {{
            "question": "What are you looking for on this website?",
            "options": [
                "A. [First main category]",
                "B. [Second main category]",
                "C. [Third main category]",
                "D. [Fourth main category]"
            ]
        }}

        Remember:
        - The question should help identify visitor intent
        - Options should be based on actual content categories
        - Options should be clear and distinct
        - Format must be valid JSON

        Response:"""

        return PromptTemplate(
            template=template,
            input_variables=["title", "meta_description", "main_content", "headings"]
        )

    # Create a prompt template for analyzing results
    def create_results_prompt(self):
        template = """Analyze the following website content, questions, and user answers to classify the user's intent.

        Website Content:
        Title: {title}
        Description: {meta_description}
        Main Content: {main_content}
        Headings: {headings}

        Questions and Answers:
        {questions_and_answers}

        Based on the content and the user's answers, classify the user's intent and provide a brief explanation.

        Response in JSON format:
        {{
            "user_intent": "[Classified user intent]",
            "explanation": "[Brief explanation]"
        }}

        Response:"""

        return PromptTemplate(
            template=template,
            input_variables=["title", "meta_description", "main_content", "headings", "questions_and_answers"]
        )

    # Analyze the content of a website and generate a question with options
    def analyze_content(self, content: Dict[str, str]) -> Dict:
        try:
            # Prepare content
            headings_text = ", ".join([h["text"] for h in content.get("headings", [])])
            
            # Create input for prompt
            prompt_input = {
                "title": content.get("title", ""),
                "meta_description": content.get("meta_description", ""),
                "main_content": content.get("main_content", "")[:1000],
                "headings": headings_text
            }

            # Create and run chain
            chain = LLMChain(llm=self.llm, prompt=self.create_questions_prompt())
            response = chain.run(prompt_input)

            # Parse JSON response
            try:
                result = json.loads(response)
                return {
                    'question_data': result,
                    'content_analysis': {
                        'website_type': self._analyze_content_type(content),
                        'primary_categories': self._extract_main_categories(content)
                    }
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                print("Failed to parse JSON, using fallback processing")
                return self._process_unstructured_response(response)

        except Exception as e:
            print(f"Error in analyze_content: {str(e)}")
            raise

    def _analyze_content_type(self, content: Dict) -> str:
        title = content.get("title", "").lower()
        main_content = content.get("main_content", "").lower()
        
        content_types = {
            "e-commerce": ["shop", "buy", "price", "store", "product"],
            "educational": ["learn", "course", "tutorial", "training"],
            "informational": ["news", "article", "blog", "info"],
            "service": ["service", "consultation", "support", "help"],
            "corporate": ["about us", "company", "business", "enterprise"]
        }
        
        for type_name, keywords in content_types.items():
            if any(word in title or word in main_content for word in keywords):
                return type_name
                
        return "general"

    def _extract_main_categories(self, content: Dict) -> List[str]:
        # Extract categories from headings and content
        headings = [h["text"] for h in content.get("headings", [])]
        
        # Simple extraction based on common patterns
        categories = set()
        
        # Check headings for potential categories
        for heading in headings:
            if any(word in heading.lower() for word in ["products", "services", "categories"]):
                categories.add(heading)
                
        return list(categories)

    def _process_unstructured_response(self, response: str) -> Dict:
        # Fallback processing if JSON parsing fails
        lines = response.split('\n')
        question = ""
        options = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('A.', 'B.', 'C.', 'D.')):
                options.append(line)
            elif line and not any(line.startswith(prefix) for prefix in ['{', '}', '"']):
                question = line
                
        return {
            'question_data': {
                'question': question,
                'options': options
            }
        }
    
    # Analyze the results of the content and the questions answered by the user
    def analyze_results(self, content: Dict, questions: List[Dict], answers: List[str], session_id: Optional[str] = None) -> Dict:
        try:
            # Save user responses first
            session_id = self.user_responses.save_user_responses(
                url=content.get('url', ''),
                questions=questions,
                answers=answers,
                session_id=session_id
            )

            # Prepare content
            headings_text = ", ".join([h["text"] for h in content.get("headings", [])])
            
            # Get stored responses
            user_response_data = self.user_responses.get_user_responses(session_id)
            questions_and_answers = "\n".join(
                [f"Q: {r['question']}\nA: {r['selected_answer']}" 
                 for r in user_response_data['responses']]
            )

            # Create input for prompt
            prompt_input = {
                "title": content.get("title", ""),
                "meta_description": content.get("meta_description", ""),
                "main_content": content.get("main_content", "")[:1000],
                "headings": headings_text,
                "questions_and_answers": questions_and_answers,
                "session_id": session_id  # Include for reference
            }

            # Create and run chain
            chain = LLMChain(llm=self.llm, prompt=self.create_results_prompt())
            response = chain.run(prompt_input)

            try:
                result = json.loads(response)
                # Add session_id to result for reference
                result['session_id'] = session_id
                return result
            except json.JSONDecodeError:
                return {
                    "user_intent": "unknown", 
                    "explanation": "Failed to parse response",
                    "session_id": session_id
                }

        except Exception as e:
            print(f"Error in analyze_results: {str(e)}")
            raise