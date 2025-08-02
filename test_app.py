#!/usr/bin/env python3
"""
Simple test script to verify MindDoc application setup
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from app import create_app
        print("✅ Flask app import successful")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    try:
        from app.services.document_processor import DocumentProcessor
        print("✅ Document processor import successful")
    except ImportError as e:
        print(f"❌ Document processor import failed: {e}")
        return False
    
    try:
        from app.services.dify_service import DifyService
        print("✅ Dify service import successful")
    except ImportError as e:
        print(f"❌ Dify service import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Test environment variables
    secret_key = os.environ.get('SECRET_KEY')
    dify_key = os.environ.get('DIFY_API_KEY')
    
    if secret_key and secret_key != 'your-secret-key-here-change-in-production':
        print("✅ SECRET_KEY configured")
    else:
        print("⚠️  SECRET_KEY not configured (using default)")
    
    if dify_key and dify_key != 'your-dify-api-key-here':
        print("✅ DIFY_API_KEY configured")
    else:
        print("⚠️  DIFY_API_KEY not configured (Dify features disabled)")
    
    return True

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_spacy():
    """Test spaCy model loading"""
    print("\nTesting spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        return True
    except OSError:
        print("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"❌ spaCy error: {e}")
        return False

def main():
    """Run all tests"""
    print("MindDoc Application Test")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_config,
        test_app_creation,
        test_spacy
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("python run.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 