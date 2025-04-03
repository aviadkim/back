#!/usr/bin/env python3
"""
Analyze the results of the comprehensive Q&A test.
This script will read the most recent test results and provide an analysis.
"""
import os
import sys
import re
from glob import glob
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QAAnalysis")

def find_latest_results():
    """Find the latest test results file"""
    results_dir = "/workspaces/back/qa_test_results"
    if not os.path.exists(results_dir):
        logger.error(f"Results directory not found: {results_dir}")
        return None
        
    result_files = glob(os.path.join(results_dir, "comprehensive_qa_test_*.txt"))
    if not result_files:
        logger.error("No test result files found")
        return None
        
    # Sort by modification time, newest first
    result_files.sort(key=os.path.getmtime, reverse=True)
    return result_files[0]

def parse_results(file_path):
    """Parse the test results file"""
    logger.info(f"Analyzing results from: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract metadata
    metadata = {}
    match = re.search(r'Document ID: (.*?)\n', content)
    if match:
        metadata['document_id'] = match.group(1)
        
    match = re.search(r'Document Path: (.*?)\n', content)
    if match:
        metadata['document_path'] = match.group(1)
        
    match = re.search(r'Date: (.*?)\n', content)
    if match:
        metadata['date'] = match.group(1)
    
    # Parse Q&A pairs
    qa_pattern = r'Q(\d+): (.*?)\nA: (.*?)(?=\n\nQ\d+:|$)'
    qa_pairs = re.findall(qa_pattern, content, re.DOTALL)
    
    results = []
    for num, question, answer in qa_pairs:
        results.append({
            'number': int(num),
            'question': question.strip(),
            'answer': answer.strip(),
            'analysis': analyze_answer(answer.strip())
        })
    
    return metadata, results

def analyze_answer(answer):
    """Analyze the quality of an answer"""
    # Check for error responses
    if answer.startswith("Error:"):
        return {
            'status': 'error',
            'quality': 0,
            'notes': 'API error occurred'
        }
    
    # Check for fallback responses
    fallback_phrases = [
        "I couldn't find",
        "I couldn't determine",
        "I don't have enough information",
        "Not enough information",
        "The document doesn't mention",
        "I couldn't locate"
    ]
    
    for phrase in fallback_phrases:
        if phrase.lower() in answer.lower():
            return {
                'status': 'fallback',
                'quality': 1,
                'notes': 'Fallback response used'
            }
    
    # Check for short answers (likely too simple)
    if len(answer) < 30:
        return {
            'status': 'short',
            'quality': 2,
            'notes': 'Answer is very brief'
        }
    
    # Check for detailed answers with specific information
    if re.search(r'\d+%|\$[\d,.]+|[\d,.]+ USD|ISIN [A-Z0-9]+', answer):
        return {
            'status': 'detailed',
            'quality': 4,
            'notes': 'Contains specific data points'
        }
    
    # Default: moderate answer
    return {
        'status': 'moderate',
        'quality': 3,
        'notes': 'Generic but reasonable response'
    }

def generate_report(metadata, results):
    """Generate a comprehensive analysis report"""
    total_questions = len(results)
    
    # Count by status
    status_counts = {
        'error': 0,
        'fallback': 0,
        'short': 0,
        'moderate': 0,
        'detailed': 0
    }
    
    for result in results:
        status = result['analysis']['status']
        status_counts[status] += 1
    
    # Calculate average quality
    avg_quality = sum(r['analysis']['quality'] for r in results) / total_questions
    
    # Identify best and worst answers
    results_by_quality = sorted(results, key=lambda r: r['analysis']['quality'])
    worst_answers = results_by_quality[:3]
    best_answers = results_by_quality[-3:]
    
    # Generate report
    print("\n" + "="*60)
    print(f"DOCUMENT Q&A ANALYSIS REPORT")
    print("="*60)
    print(f"Document ID: {metadata.get('document_id', 'Unknown')}")
    print(f"Document: {os.path.basename(metadata.get('document_path', 'Unknown'))}")
    print(f"Test Date: {metadata.get('date', 'Unknown')}")
    print(f"Total Questions: {total_questions}")
    print("="*60)
    
    print("\nRESPONSE QUALITY SUMMARY:")
    print(f"- Average Answer Quality: {avg_quality:.2f}/4.0")
    print(f"- Detailed Responses: {status_counts['detailed']} ({status_counts['detailed']/total_questions*100:.1f}%)")
    print(f"- Moderate Responses: {status_counts['moderate']} ({status_counts['moderate']/total_questions*100:.1f}%)")
    print(f"- Short Responses: {status_counts['short']} ({status_counts['short']/total_questions*100:.1f}%)")
    print(f"- Fallback Responses: {status_counts['fallback']} ({status_counts['fallback']/total_questions*100:.1f}%)")
    print(f"- Error Responses: {status_counts['error']} ({status_counts['error']/total_questions*100:.1f}%)")
    
    print("\nBEST ANSWERS:")
    for i, result in enumerate(reversed(best_answers), 1):
        print(f"\n{i}. Q: {result['question']}")
        print(f"   A: {result['answer'][:100]}..." if len(result['answer']) > 100 else f"   A: {result['answer']}")
        print(f"   Quality: {result['analysis']['quality']}/4 ({result['analysis']['status']})")
    
    print("\nAREAS FOR IMPROVEMENT:")
    for i, result in enumerate(worst_answers, 1):
        print(f"\n{i}. Q: {result['question']}")
        print(f"   A: {result['answer'][:100]}..." if len(result['answer']) > 100 else f"   A: {result['answer']}")
        print(f"   Quality: {result['analysis']['quality']}/4 ({result['analysis']['status']})")
    
    print("\nMODEL PERFORMANCE ANALYSIS:")
    if avg_quality >= 3.5:
        print("✅ EXCELLENT: The model is providing detailed and accurate responses.")
        print("   The AI integration is working very well.")
    elif avg_quality >= 2.5:
        print("✅ GOOD: The model is providing reasonable responses for most questions.")
        print("   Consider fine-tuning for more detailed answers.")
    elif avg_quality >= 1.5:
        print("⚠️ FAIR: The model is struggling with some questions.")
        print("   Consider checking the API integration and document processing.")
    else:
        print("❌ POOR: The model is failing to provide useful answers.")
        print("   The API integration may be broken or the model is not suitable.")
    
    print("\n" + "="*60)
    
    # Save report to file
    report_file = os.path.splitext(metadata['document_path'])[0] + "_analysis.txt"
    with open(report_file, 'w') as f:
        f.write("DOCUMENT Q&A ANALYSIS REPORT\n")
        f.write(f"Document ID: {metadata.get('document_id', 'Unknown')}\n")
        f.write(f"Document: {os.path.basename(metadata.get('document_path', 'Unknown'))}\n")
        f.write(f"Test Date: {metadata.get('date', 'Unknown')}\n")
        f.write(f"Total Questions: {total_questions}\n\n")
        
        f.write("DETAILED RESULTS:\n\n")
        for result in results:
            f.write(f"Q{result['number']}: {result['question']}\n")
            f.write(f"A: {result['answer']}\n")
            f.write(f"Analysis: {result['analysis']['status']} (Quality: {result['analysis']['quality']}/4)\n\n")
    
    logger.info(f"Detailed analysis saved to: {report_file}")

def main():
    """Main function"""
    # Find latest results file
    results_file = find_latest_results()
    if not results_file:
        return 1
        
    # Parse and analyze results
    metadata, results = parse_results(results_file)
    
    # Generate report
    generate_report(metadata, results)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
