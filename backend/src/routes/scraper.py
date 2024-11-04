from flask import Blueprint, request, jsonify
from src.services.web_scraping import WebScraper
from src.services.ai_analyzer import AIAnalyzer
from src.services.analysis_cache import URLQuestionsCache

scraper_bp = Blueprint('scraper', __name__)
web_scraper = WebScraper()
ai_analyzer = AIAnalyzer()
questions_cache = URLQuestionsCache()

@scraper_bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Check cache for existing questions
        cached_questions = questions_cache.get_questions(url)
        if cached_questions:
            return jsonify({'questions': cached_questions})

        # Scrape website if no cached questions
        content = web_scraper.scrape_website(url)
        
        # Generate question with options
        analysis = ai_analyzer.analyze_content(content)
        
        # Save questions to cache
        questions_cache.save_questions(url, analysis['question_data']['options'])
        
        return jsonify({
            'content': content,
            'questions': analysis['question_data']
        })

    except Exception as e:
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

        # Analyze results
        results = ai_analyzer.analyze_results(content, questions, user_answers)
        
        return jsonify({
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500