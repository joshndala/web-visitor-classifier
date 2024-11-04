import boto3
from datetime import datetime
from typing import Dict, List, Optional

class URLQuestionsCache:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('website-analyses')

    def save_questions(self, url: str, questions: List[Dict]) -> Dict:
        """
        Save multiple questions for a URL
        Example questions format:
        [
            {
                'question': 'Which product category interests you?',
                'options': ['A. Mac', 'B. iPad', 'C. iPhone', 'D. Watch']
            },
            {
                'question': 'What is your experience level?',
                'options': ['A. Beginner', 'B. Intermediate', 'C. Advanced', 'D. Expert']
            }
        ]
        """
        item = {
            'url': url,
            'timestamp': datetime.now(datetime.timezone.utc),
            'questions': questions
        }
        
        return self.table.put_item(Item=item)

    def get_questions(self, url: str) -> Optional[Dict]:
        """
        Get all questions for a URL
        Returns None if URL hasn't been analyzed
        """
        response = self.table.query(
            KeyConditionExpression='url = :url',
            ExpressionAttributeValues={
                ':url': url
            },
            ScanIndexForward=False  # Most recent first
        )
        
        return response.get('Items', [])
    
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