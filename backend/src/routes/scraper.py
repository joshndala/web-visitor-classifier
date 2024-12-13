from flask import Blueprint, request, jsonify
from src.services.web_scraping import WebScraper
from src.services.ai_analyzer import AIAnalyzer
from src.services.analysis_cache import URLQuestionsCache
import json

scraper_bp = Blueprint('scraper', __name__)
web_scraper = WebScraper()
ai_analyzer = AIAnalyzer()  # This will now be our Bedrock-based analyzer
questions_cache = URLQuestionsCache()

@scraper_bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    try:
        print("Received generate-questions request")
        data = request.get_json()
        url = data.get('url')
        print(f"Processing URL: {url}")
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Scrape website
        print("Starting web scraping...")
        content = web_scraper.scrape_website(url)
        print("Scraping complete, content length:", len(str(content)))
        
        # Generate question with options using Bedrock
        print("Starting content analysis...")
        analysis = ai_analyzer.analyze_content(content)
        print("Analysis complete:", analysis)
        
        return jsonify({
            'content': content,
            'questions': analysis['question_data']
        })

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return jsonify({'error': 'Failed to parse model response'}), 500
    except Exception as e:
        print(f"Unexpected error in generate_questions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraper_bp.route('/analyze-results', methods=['POST'])
def analyze_results():
    try:
        data = request.get_json()
        content = data.get('content')
        questions = data.get('questions')
        user_answers = data.get('answers', [])
        
        if not content or not questions or not user_answers:
            return jsonify({'error': 'Content, questions, and answers are required'}), 400

        # Analyze results using Bedrock
        results = ai_analyzer.analyze_results(content, questions, user_answers)
        
        return jsonify({
            'results': results
        })

    except json.JSONDecodeError as e:
        return jsonify({'error': 'Failed to parse model response'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500