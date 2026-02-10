"""
Test script for advanced PatternDetector (Semantic Clustering).
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pattern_detector import PatternDetector

def main():
    print("=== PatternDetector Semantic Clustering Test ===\n")
    
    # Enable ML if deps are present
    detector = PatternDetector(use_ml=True)
    if not detector.use_ml:
        print("ML dependencies not found, skipping semantic test.")
        return

    # Sample error logs (some related, some not)
    error_logs = [
        {"message": "NameError: name 'user_id' is not defined"},
        {"message": "NameError: name 'user_id' is not defined"}, # Exact match (Heuristic)
        {"message": "AttributeError: 'NoneType' object has no attribute 'get_data'"},
        {"message": "AttributeError: 'NoneType' object has no attribute 'get_user'"}, # Semantic match to above
        {"message": "ConnectionError: Failed to connect to server at localhost:8000"},
        {"message": "ConnectionError: Could not reach the server on 127.0.0.1:8000"}, # Semantic match to above
        {"message": "SyntaxError: invalid syntax at line 42"},
    ]
    
    print(f"Analyzing {len(error_logs)} error logs...")
    patterns = detector.analyze_errors(error_logs)
    
    print(f"\nDetected {len(patterns)} patterns:\n")
    for pat in patterns:
        print(f"[{pat.category.upper()}] ID: {pat.id}")
        print(f" Description: {pat.description}")
        print(f" Frequency: {pat.frequency}")
        print(f" Confidence: {pat.confidence}")
        print(f" Suggested Fix: {pat.suggested_fix}")
        print(f" Examples: {pat.examples}")
        print("-" * 30)

if __name__ == "__main__":
    main()
