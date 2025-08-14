import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from phonetic_fuzzer import PhoneticFuzzer, Hazer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize the phonetic fuzzer and hazer
fuzzer = PhoneticFuzzer()
hazer = Hazer()

# Supported languages
LANGUAGES = {
    'english': 'English',
    'spanish': 'Spanish',
    'french': 'French',
    'german': 'German',
    'italian': 'Italian',
    'portuguese': 'Portuguese'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for the phonetic fuzzing interface."""
    if request.method == 'POST':
        try:
            # Get the input text and language parameters
            input_text = request.form.get('input_text', '').strip()
            lang_a = request.form.get('lang_a', 'english')
            lang_b = request.form.get('lang_b', 'spanish')
            method = request.form.get('method', 'hybrid')
            
            if not input_text:
                flash('Please enter some text to process.', 'warning')
                return redirect(url_for('index'))
            
            if len(input_text) > 5000:
                flash('Text too long. Please limit input to 5000 characters.', 'error')
                return redirect(url_for('index'))
            
            # Validate languages
            if lang_a not in LANGUAGES or lang_b not in LANGUAGES:
                flash('Invalid language selection.', 'error')
                return redirect(url_for('index'))
            
            if lang_a == lang_b:
                flash('Please select different source and target languages.', 'warning')
                return redirect(url_for('index'))
            
            # Process the text through cross-language phonetic hazing
            if method == 'hybrid':
                results = hazer.hybrid_haze(input_text, lang_a, lang_b)
            else:
                results = hazer.haze(input_text, lang_a, lang_b, method=method)
            
            # Format results for the template
            processed_results = format_results_for_template(results, input_text)
            
            return render_template('index.html', 
                                 input_text=input_text,
                                 lang_a=lang_a,
                                 lang_b=lang_b,
                                 method=method,
                                 results=processed_results,
                                 languages=LANGUAGES)
            
        except Exception as e:
            logging.error(f"Error processing text: {str(e)}")
            flash(f'An error occurred while processing your text: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('index.html', languages=LANGUAGES)

def format_results_for_template(results, input_text):
    """Format hazer results for the template."""
    processed_words = []
    
    for word_detail in results.get('word_transformations', []):
        variations = [
            {
                'text': word_detail['original'],
                'similarity': 1.0,
                'confidence': 'Original'
            },
            {
                'text': word_detail['transformed'],
                'similarity': 0.8,  # Approximate similarity
                'confidence': 'High'
            }
        ]
        
        processed_words.append({
            'original': word_detail['original'],
            'variations': variations,
            'transformation_chain': word_detail.get('chain', '')
        })
    
    return {
        'original_text': input_text,
        'transformed_text': results.get('transformed_sentence', ''),
        'method': results.get('method', ''),
        'language_route': results.get('language_route', ''),
        'word_count': results.get('word_count', 0),
        'processed_words': processed_words,
        'summary': {
            'total_variations': len(processed_words) * 2,  # original + transformed
            'avg_similarity': 0.85
        }
    }

@app.route('/api/fuzz', methods=['POST'])
def api_fuzz():
    """API endpoint for cross-language phonetic hazing."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        input_text = data['text'].strip()
        lang_a = data.get('lang_a', 'english')
        lang_b = data.get('lang_b', 'spanish')
        method = data.get('method', 'fuzzy')
        
        if not input_text:
            return jsonify({'error': 'Empty text provided'}), 400
            
        if len(input_text) > 5000:
            return jsonify({'error': 'Text too long. Limit: 5000 characters'}), 400
        
        # Validate languages
        if lang_a not in LANGUAGES or lang_b not in LANGUAGES:
            return jsonify({'error': 'Invalid language selection'}), 400
            
        if lang_a == lang_b:
            return jsonify({'error': 'Source and target languages must be different'}), 400
        
        # Process the text
        if method == 'hybrid':
            results = hazer.hybrid_haze(input_text, lang_a, lang_b)
        else:
            results = hazer.haze(input_text, lang_a, lang_b, method=method)
        
        formatted_results = format_results_for_template(results, input_text)
        return jsonify({'results': formatted_results})
        
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logging.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html'), 500
