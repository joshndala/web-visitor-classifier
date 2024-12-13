import boto3
import json

def test_bedrock_connection():
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        test_prompt = "Hi, this is a test message. Please respond with a short greeting."
        
        response = bedrock.invoke_model(
            modelId='us.meta.llama3-2-3b-instruct-v1:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": test_prompt,
                "temperature": 0.3
            })
        )
        
        response_body = json.loads(response['body'].read())
        print("Connection successful!")
        print("Model response:", response_body)
        
    except Exception as e:
        print("Error:", str(e))

test_bedrock_connection()