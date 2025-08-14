# Cross-Language Phonetic Hazer

## Overview

This is a web-based cross-language phonetic transformation tool built with Flask using the existing Hazer algorithm. The application transforms text through a bridge language using phonetic rules (Source → Bridge → Source) to reveal hidden phonetic similarities across languages. Users can select source/bridge languages, choose transformation methods (Fuzzy, Translation, Hybrid), and view detailed results with similarity scores.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Lightweight Python web framework chosen for its simplicity and flexibility
- **Template Engine**: Jinja2 templates for server-side rendering with Bootstrap for responsive UI
- **Static Assets**: CSS styling with Bootstrap Dark theme and custom styles

### Core Processing Engine
- **Hazer Class**: Central component that handles cross-language phonetic transformations
- **Bridge Language System**: Transforms text: Source → Bridge → Source using phonetic rules
- **Hybrid Transformation Method**: Smart processing that combines phonetic transformation with Google Translate fallback for optimal cross-language results
- **Language Support**: English, Spanish, French, German, Italian, Portuguese with automatic detection

### Application Structure
- **Web Interface**: Complete form with language selection and text input
- **Results Display**: Shows transformed text, transformation chain, and detailed word analysis
- **Error Handling**: Comprehensive try-catch blocks with user-friendly flash messages
- **Input Validation**: Text length limits (5000 characters) and sanitization
- **Copy Functionality**: JavaScript clipboard integration for easy result copying

### Frontend Design
- **Bootstrap 5**: Dark theme for modern UI experience
- **Responsive Layout**: Mobile-friendly design with proper viewport configuration
- **Interactive Elements**: Hover effects, transitions, and visual feedback
- **Typography**: Monospace fonts for phonetic variations to improve readability

### Security Considerations
- **Session Management**: Secret key configuration with environment variable support
- **Input Sanitization**: Form data validation and length restrictions
- **Error Isolation**: Safe error handling that doesn't expose system details

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **googletrans**: Google Translate API integration for translation method
- **requests**: HTTP requests for external API calls
- **difflib**: Text similarity comparison (Python standard library)
- **re**: Regular expression processing (Python standard library)
- **logging**: Application logging (Python standard library)

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme variant
- **Bootstrap Icons**: Icon library for enhanced user interface
- **Custom CSS**: Additional styling for phonetic display and interactions

### Development Environment
- **Replit hosting**: Configured to run on host 0.0.0.0:5000 for cloud deployment
- **Environment variables**: SESSION_SECRET for production security
- **Debug mode**: Enabled for development with comprehensive error reporting