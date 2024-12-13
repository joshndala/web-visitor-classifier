import boto3
import json
from typing import Dict

class AIAnalyzer:
    def __init__(self):
        self.bedrock = boto3.client(
            service_name = 'bedrock-runtime',
            region_name = 'us-east-1'
            )
        
        self.modelId = 'us.meta.llama3-2-3b-instruct-v1:0'
    
    def analyze_content(self, content: Dict[str, str]) -> Dict:
        try:
            print("Starting content analysis...")
            
            # Verify content structure
            print("Content received:", {k: type(v) for k, v in content.items()})
            
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>You are a helpful assistant that analyzes website content and creates multiple-choice questions.<|eot_id|><|start_header_id|>user<|end_header_id|>Analyze this website content and create a single multiple-choice question:

            Website Content:
            Title: {content.get('title', '')}
            Description: {content.get('meta_description', '')}
            Main Content: {content.get('main_content', '')[:1000]}
            Headings: {', '.join([h['text'] for h in content.get('headings', [])])}

            Return ONLY a JSON object with this exact structure:
            {{
                "question": "What are you looking for on this website?",
                "options": [
                    "A. [First option]",
                    "B. [Second option]",
                    "C. [Third option]",
                    "D. [Fourth option]"
                ]
            }}
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            print("Prompt created, sending to model...")
            
            try:
                response = self.bedrock.invoke_model(
                    modelId=self.modelId,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "prompt": prompt,
                        "temperature": 0.3,
                        "top_p": 0.7
                    })
                )
                print("Raw response received from model")
            except Exception as e:
                print(f"Error calling Bedrock: {str(e)}")
                raise

            try:
                print("Attempting to read response body...")
                response_body = json.loads(response['body'].read().decode('utf-8'))
                print("Response body decoded:", response_body)
                generated_text = response_body.get('generation', '')
                print("Generated text:", generated_text)
            except Exception as e:
                print(f"Error processing response body: {str(e)}")
                raise

            try:
                # Try to find and parse the JSON object in the response
                start_idx = generated_text.find('{')
                end_idx = generated_text.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    print("Could not find JSON markers in response")
                    raise ValueError("No JSON object found in response")
                    
                json_str = generated_text[start_idx:end_idx]
                print("Extracted JSON string:", json_str)
                
                question_data = json.loads(json_str)
                print("Successfully parsed question data:", question_data)
                
                return {
                    'question_data': question_data
                }
                
            except Exception as e:
                print(f"Error parsing generated text: {str(e)}")
                print("Falling back to default response")
                return {
                    'question_data': {
                        'question': 'What are you looking for on this website?',
                        'options': [
                            'A. College Application Guidance',
                            'B. Scholarship Information',
                            'C. Essay Writing Help',
                            'D. Interview Preparation'
                        ]
                    }
                }
                
        except Exception as e:
            print(f"Unexpected error in analyze_content: {str(e)}")
            raise