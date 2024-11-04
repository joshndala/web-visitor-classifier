from flask import Blueprint, request, jsonify
from src.services.web_scraping import WebScraper
from src.services.ai_analyzer import AIAnalyzer

scraper_bp = Blueprint('scraper', __name__)
web_scraper = WebScraper()
ai_analyzer = AIAnalyzer()

@scraper_bp.route('/analyze', methods=['POST'])
def analyze_website():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Scrape website
        content = web_scraper.scrape_website(url)
        
        # Generate question with options
        analysis = ai_analyzer.analyze_content(content)
        
        return jsonify({
            'content': content,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500