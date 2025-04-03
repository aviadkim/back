import requests
import time
import statistics
import concurrent.futures
import argparse

BASE_URL = "http://localhost:5001"

def test_endpoint(endpoint, method="GET", data=None, files=None, iterations=10):
    """Test the performance of an endpoint"""
    times = []
    errors = 0
    
    for i in range(iterations):
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, files=files)
            
            if response.status_code >= 400:
                errors += 1
        except Exception as e:
            errors += 1
        finally:
            end_time = time.time()
            times.append(end_time - start_time)
    
    return {
        "endpoint": endpoint,
        "method": method,
        "iterations": iterations,
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "median_time": statistics.median(times),
        "errors": errors
    }

def test_concurrent_users(endpoint, concurrent_users=10, method="GET", data=None):
    """Test the endpoint with concurrent users"""
    start_time = time.time()
    errors = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for _ in range(concurrent_users):
            if method == "GET":
                futures.append(executor.submit(requests.get, f"{BASE_URL}{endpoint}"))
            elif method == "POST":
                futures.append(executor.submit(requests.post, f"{BASE_URL}{endpoint}", json=data))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                response = future.result()
                if response.status_code >= 400:
                    errors += 1
            except Exception:
                errors += 1
    
    end_time = time.time()
    
    return {
        "endpoint": endpoint,
        "method": method,
        "concurrent_users": concurrent_users,
        "total_time": end_time - start_time,
        "errors": errors
    }

def main():
    parser = argparse.ArgumentParser(description="Performance testing for Financial Document API")
    parser.add_argument("--concurrent", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")
    args = parser.parse_args()
    
    print("Performance Testing Financial Document API")
    print("=========================================")
    
    # Test basic endpoints
    endpoints = [
        "/health",
        "/api/documents"
    ]
    
    print("\nTesting basic endpoints:")
    for endpoint in endpoints:
        result = test_endpoint(endpoint, iterations=args.iterations)
        print(f"  {result['method']} {result['endpoint']}: Avg: {result['avg_time']:.3f}s, Min: {result['min_time']:.3f}s, Max: {result['max_time']:.3f}s, Errors: {result['errors']}")
    
    # Get a document ID for testing
    response = requests.get(f"{BASE_URL}/api/documents")
    documents = response.json().get('documents', [])
    
    if documents:
        document_id = documents[0]['document_id']
        
        print("\nTesting document-specific endpoints:")
        document_endpoints = [
            f"/api/documents/{document_id}",
            f"/api/documents/{document_id}/content",
            f"/api/documents/{document_id}/financial",
            f"/api/documents/{document_id}/tables",
            f"/api/documents/{document_id}/advanced_analysis"
        ]
        
        for endpoint in document_endpoints:
            result = test_endpoint(endpoint, iterations=args.iterations)
            print(f"  {result['method']} {endpoint}: Avg: {result['avg_time']:.3f}s, Min: {result['min_time']:.3f}s, Max: {result['max_time']:.3f}s, Errors: {result['errors']}")
        
        # Test Q&A endpoint
        print("\nTesting Q&A endpoint:")
        qa_data = {"document_id": document_id, "question": "What ISINs are in the document?"}
        result = test_endpoint("/api/qa/ask", method="POST", data=qa_data, iterations=args.iterations)
        print(f"  {result['method']} /api/qa/ask: Avg: {result['avg_time']:.3f}s, Min: {result['min_time']:.3f}s, Max: {result['max_time']:.3f}s, Errors: {result['errors']}")
    
    # Test concurrent users
    print(f"\nTesting with {args.concurrent} concurrent users:")
    result = test_concurrent_users("/health", concurrent_users=args.concurrent)
    print(f"  {result['method']} {result['endpoint']}: Total time: {result['total_time']:.3f}s, Errors: {result['errors']}")
    
    if documents:
        result = test_concurrent_users(f"/api/documents/{document_id}", concurrent_users=args.concurrent)
        print(f"  {result['method']} {result['endpoint']}: Total time: {result['total_time']:.3f}s, Errors: {result['errors']}")

if __name__ == "__main__":
    main()
