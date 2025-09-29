#!/usr/bin/env python3
"""
Performance Tests
Tests API response times and database query performance
"""

import pytest
import requests
import time
import sqlite3
import os
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestPerformance:
    """Test cases for API and database performance"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.base_url = "http://localhost:5002"
        self.api_base = f"{self.base_url}/api"
        self.test_db_path = "data.db"
        
        # Ensure database exists
        if not os.path.exists(self.test_db_path):
            pytest.skip("Database not found. Run csv_to_sqlite.py first.")
    
    def test_api_response_times(self):
        """Test that API endpoints respond within acceptable time limits"""
        endpoints = [
            f"{self.api_base}/county_data",
            f"{self.api_base}/health_rankings",
            f"{self.api_base}/stats",
            f"{self.api_base}/location/states",
            f"{self.api_base}/location/cities"
        ]
        
        max_response_time = 2.0  # 2 seconds max
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
            assert response_time < max_response_time, f"Endpoint {endpoint} too slow: {response_time:.2f}s"
    
    def test_api_response_times_with_filters(self):
        """Test API response times with various filters"""
        test_cases = [
            f"{self.api_base}/county_data?state=CA",
            f"{self.api_base}/county_data?limit=10",
            f"{self.api_base}/health_rankings?page=1&per_page=10",
            f"{self.api_base}/search?q=Los Angeles",
            f"{self.api_base}/location/cities?state=CA&limit=5"
        ]
        
        max_response_time = 3.0  # 3 seconds max for filtered queries
        
        for endpoint in test_cases:
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
            assert response_time < max_response_time, f"Endpoint {endpoint} too slow: {response_time:.2f}s"
    
    def test_database_query_performance(self):
        """Test database query performance directly"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test basic queries
        queries = [
            "SELECT COUNT(*) FROM county_health_rankings",
            "SELECT COUNT(*) FROM zip_county",
            "SELECT COUNT(DISTINCT County) FROM county_health_rankings",
            "SELECT COUNT(DISTINCT state_abbreviation) FROM zip_county"
        ]
        
        max_query_time = 1.0  # 1 second max for basic queries
        
        for query in queries:
            start_time = time.time()
            cursor.execute(query)
            result = cursor.fetchone()
            end_time = time.time()
            
            query_time = end_time - start_time
            assert query_time < max_query_time, f"Query too slow: {query} took {query_time:.2f}s"
            assert result[0] > 0, f"Query returned no results: {query}"
        
        # Test complex queries
        complex_queries = [
            """
            SELECT z.county, z.state_abbreviation, COUNT(z.col__zip) as zip_count
            FROM zip_county z
            GROUP BY z.county, z.state_abbreviation
            ORDER BY zip_count DESC
            LIMIT 10
            """,
            """
            SELECT h.County, h.State, h.Measure_name, h.Raw_value
            FROM county_health_rankings h
            WHERE h.Measure_name = 'Adult obesity'
            ORDER BY CAST(h.Raw_value AS REAL) DESC
            LIMIT 10
            """,
            """
            SELECT 
                z.state_abbreviation,
                COUNT(DISTINCT z.county) as county_count,
                COUNT(z.col__zip) as zip_count
            FROM zip_county z
            GROUP BY z.state_abbreviation
            ORDER BY county_count DESC
            """
        ]
        
        max_complex_query_time = 2.0  # 2 seconds max for complex queries
        
        for query in complex_queries:
            start_time = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            end_time = time.time()
            
            query_time = end_time - start_time
            assert query_time < max_complex_query_time, f"Complex query too slow: took {query_time:.2f}s"
            assert len(results) > 0, f"Complex query returned no results"
        
        conn.close()
    
    def test_concurrent_api_requests(self):
        """Test API performance under concurrent load"""
        endpoint = f"{self.api_base}/county_data"
        num_requests = 10
        max_total_time = 10.0  # 10 seconds max for all requests
        
        def make_request():
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Check total time
        assert total_time < max_total_time, f"Concurrent requests too slow: {total_time:.2f}s"
        
        # Check individual results
        successful_requests = sum(1 for r in results if r['success'])
        assert successful_requests == num_requests, f"Only {successful_requests}/{num_requests} requests succeeded"
        
        # Check response times
        response_times = [r['response_time'] for r in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.2f}s"
        assert max_response_time < 5.0, f"Max response time too high: {max_response_time:.2f}s"
    
    def test_pagination_performance(self):
        """Test pagination performance with large datasets"""
        endpoint = f"{self.api_base}/health_rankings"
        
        # Test different page sizes
        page_sizes = [10, 20, 50]
        max_response_time = 3.0
        
        for per_page in page_sizes:
            start_time = time.time()
            response = requests.get(f"{endpoint}?page=1&per_page={per_page}")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200, f"Pagination failed for per_page={per_page}"
            assert response_time < max_response_time, f"Pagination too slow for per_page={per_page}: {response_time:.2f}s"
            
            data = response.json()
            assert len(data['data']) <= per_page, f"Returned more items than requested: {len(data['data'])} > {per_page}"
    
    def test_search_performance(self):
        """Test search performance with various query types"""
        search_endpoint = f"{self.api_base}/search"
        
        test_queries = [
            "Los Angeles",
            "New York",
            "California",
            "90210",
            "County",
            "a"  # Single character search
        ]
        
        max_response_time = 2.0
        
        for query in test_queries:
            start_time = time.time()
            response = requests.get(f"{search_endpoint}?q={query}")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200, f"Search failed for query: {query}"
            assert response_time < max_response_time, f"Search too slow for query '{query}': {response_time:.2f}s"
            
            data = response.json()
            assert data['success'] is True, f"Search returned error for query: {query}"
    
    def test_database_connection_pooling(self):
        """Test database connection handling"""
        # Test multiple rapid connections
        connections = []
        max_connection_time = 0.1  # 100ms max per connection
        
        try:
            for i in range(10):
                start_time = time.time()
                conn = sqlite3.connect(self.test_db_path)
                end_time = time.time()
                
                connection_time = end_time - start_time
                assert connection_time < max_connection_time, f"Connection {i} too slow: {connection_time:.2f}s"
                
                # Test basic query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                connections.append(conn)
            
            # Test concurrent connections
            def test_connection():
                conn = sqlite3.connect(self.test_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
                result = cursor.fetchone()
                conn.close()
                return result[0]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(test_connection) for _ in range(5)]
                results = [future.result() for future in as_completed(futures)]
            
            # All connections should return the same result
            assert all(r == results[0] for r in results), "Concurrent connections returned different results"
            
        finally:
            # Clean up connections
            for conn in connections:
                conn.close()
    
    def test_memory_usage(self):
        """Test that API doesn't consume excessive memory"""
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make several API requests
        endpoints = [
            f"{self.api_base}/county_data",
            f"{self.api_base}/health_rankings",
            f"{self.api_base}/stats",
            f"{self.api_base}/location/states"
        ]
        
        for endpoint in endpoints:
            for _ in range(5):
                response = requests.get(endpoint)
                assert response.status_code == 200
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        max_memory_increase = 50 * 1024 * 1024  # 50MB
        assert memory_increase < max_memory_increase, f"Memory usage increased too much: {memory_increase / 1024 / 1024:.1f}MB"
    
    def test_large_response_handling(self):
        """Test handling of large responses"""
        # Test getting all counties
        response = requests.get(f"{self.api_base}/county_data")
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        
        # Response should be reasonable size
        response_size = len(response.content)
        max_response_size = 5 * 1024 * 1024  # 5MB
        assert response_size < max_response_size, f"Response too large: {response_size / 1024 / 1024:.1f}MB"
        
        # Test large health rankings response
        response = requests.get(f"{self.api_base}/health_rankings?per_page=50")
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        assert len(data['data']) <= 50
    
    def test_error_response_performance(self):
        """Test that error responses are also fast"""
        error_endpoints = [
            f"{self.api_base}/county_data/NonExistentCounty",
            f"{self.api_base}/zip/99999",
            f"{self.api_base}/search?q=",
            f"{self.api_base}/location/states/XX"
        ]
        
        max_error_response_time = 1.0
        
        for endpoint in error_endpoints:
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Error responses should also be fast
            assert response_time < max_error_response_time, f"Error response too slow for {endpoint}: {response_time:.2f}s"
            
            # Should return valid JSON even for errors
            try:
                data = response.json()
                assert 'success' in data or 'error' in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for error endpoint: {endpoint}")


if __name__ == "__main__":
    pytest.main([__file__])
