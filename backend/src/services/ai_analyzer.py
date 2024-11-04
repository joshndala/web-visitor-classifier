from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain import PromptTemplate, LLMChain
from langchain.llms import HuggingFacePipeline
from typing import Dict, List
import torch
import json

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
        
    def _create_prompt(self):
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
            chain = LLMChain(llm=self.llm, prompt=self._create_prompt())
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