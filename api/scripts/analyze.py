"""
Python script to analyze sentiment
Called from TypeScript API
"""
import sys
import json
import os
import pickle

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.app import SentimentAnalyzer

def main():
    if len(sys.argv) < 4:
        print(json.dumps({
            "error": "Missing arguments",
            "message": "Usage: python analyze.py <text> <model_path> <vectorizer_path>"
        }))
        sys.exit(1)
    
    text = sys.argv[1]
    model_path = sys.argv[2]
    vectorizer_path = sys.argv[3]
    
    try:
        # Load analyzer
        analyzer = SentimentAnalyzer(model_path, vectorizer_path)
        
        # Analyze
        result = analyzer.analyze(text)
        
        # Output JSON
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "message": "Failed to analyze sentiment"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()


