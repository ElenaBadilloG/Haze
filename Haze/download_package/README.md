# Cross-Language Phonetic Hazer

A Flask web application for cross-language phonetic transformations using the Hazer algorithm.

## Setup Instructions

1. Install Python 3.11+
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Open browser to http://localhost:5000

## Files Structure

- `app.py` - Main Flask application
- `main.py` - Entry point  
- `phonetic_fuzzer.py` - Core Hazer algorithm
- `templates/index.html` - Web interface
- `static/style.css` - Styling
- `requirements.txt` - Dependencies list
- `pyproject.toml` - Project configuration

## Usage

Select source and bridge languages, enter text, and transform using hybrid phonetic analysis that reveals phonetic similarities across languages.

## Features

- Cross-language phonetic transformation (Source → Bridge → Source)
- Support for English, Spanish, French, German, Italian, Portuguese
- Hybrid method combining phonetic rules with translation fallback
- Web interface with Bootstrap dark theme
- Copy-to-clipboard functionality for results
- Detailed similarity scoring and transformation chains