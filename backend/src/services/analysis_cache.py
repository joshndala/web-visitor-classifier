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