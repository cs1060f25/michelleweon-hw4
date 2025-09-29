#!/usr/bin/env python3
"""
SQL Injection Security Tests
Tests API endpoints for SQL injection vulnerabilities
"""

import pytest
import requests
import json
import sqlite3
import os


class TestSQLInjection:
    """Test cases for SQL injection protection"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.base_url = "http://localhost:5002"
        self.api_base = f"{self.base_url}/api"
        self.test_db_path = "data.db"
        
        # Ensure database exists
        if not os.path.exists(self.test_db_path):
            pytest.skip("Database not found. Run csv_to_sqlite.py first.")
    
    def test_county_data_sql_injection_state(self):
        """Test county_data endpoint against SQL injection in state parameter"""
        # Common SQL injection payloads
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; INSERT INTO zip_county VALUES ('hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked'); --",
            "' OR 1=1 --",
            "'; DELETE FROM zip_county; --",
            "' AND 1=0 UNION SELECT password FROM users --",
            "'; UPDATE zip_county SET county='hacked'; --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/county_data?state={payload}")
            
            # Should not return 500 error (indicates SQL error)
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
            
            # Should not return unexpected data
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    # Check that no data contains "hacked" (from injection attempts)
                    for item in data["data"]:
                        for value in item.values():
                            if isinstance(value, str):
                                assert "hacked" not in value.lower(), f"Data corruption detected with payload: {payload}"
    
    def test_county_data_sql_injection_limit(self):
        """Test county_data endpoint against SQL injection in limit parameter"""
        injection_payloads = [
            "1; DROP TABLE zip_county; --",
            "1 UNION SELECT * FROM sqlite_master --",
            "1; INSERT INTO zip_county VALUES ('hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked'); --",
            "1 OR 1=1 --",
            "1; DELETE FROM zip_county; --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/county_data?limit={payload}")
            
            # Should handle gracefully (either 400 or 200 with valid response)
            assert response.status_code in [200, 400], f"Unexpected status code for payload: {payload}"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert "success" in data
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_county_details_sql_injection_county_name(self):
        """Test county_details endpoint against SQL injection in county name"""
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; INSERT INTO zip_county VALUES ('hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked'); --",
            "'; DELETE FROM zip_county; --",
            "' AND 1=0 UNION SELECT password FROM users --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/county_data/{payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_county_details_sql_injection_state(self):
        """Test county_details endpoint against SQL injection in state parameter"""
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; DELETE FROM zip_county; --"
        ]
        
        # Use a valid county name with malicious state parameter
        valid_county = "Los Angeles"
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/county_data/{valid_county}?state={payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_zip_info_sql_injection_zip_code(self):
        """Test zip_info endpoint against SQL injection in zip code"""
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; INSERT INTO zip_county VALUES ('hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked'); --",
            "'; DELETE FROM zip_county; --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/zip/{payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_health_rankings_sql_injection_filters(self):
        """Test health_rankings endpoint against SQL injection in filter parameters"""
        injection_payloads = [
            "'; DROP TABLE county_health_rankings; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; DELETE FROM county_health_rankings; --"
        ]
        
        for payload in injection_payloads:
            # Test county parameter
            response = requests.get(f"{self.api_base}/health_rankings?county={payload}")
            assert response.status_code != 500, f"SQL injection successful in county parameter: {payload}"
            
            # Test state parameter
            response = requests.get(f"{self.api_base}/health_rankings?state={payload}")
            assert response.status_code != 500, f"SQL injection successful in state parameter: {payload}"
            
            # Test both parameters together
            response = requests.get(f"{self.api_base}/health_rankings?county={payload}&state={payload}")
            assert response.status_code != 500, f"SQL injection successful with both parameters: {payload}"
    
    def test_health_rankings_sql_injection_pagination(self):
        """Test health_rankings endpoint against SQL injection in pagination parameters"""
        injection_payloads = [
            "1; DROP TABLE county_health_rankings; --",
            "1 UNION SELECT * FROM sqlite_master --",
            "1; DELETE FROM county_health_rankings; --",
            "1 OR 1=1 --"
        ]
        
        for payload in injection_payloads:
            # Test page parameter
            response = requests.get(f"{self.api_base}/health_rankings?page={payload}")
            assert response.status_code != 500, f"SQL injection successful in page parameter: {payload}"
            
            # Test per_page parameter
            response = requests.get(f"{self.api_base}/health_rankings?per_page={payload}")
            assert response.status_code != 500, f"SQL injection successful in per_page parameter: {payload}"
    
    def test_search_sql_injection_query(self):
        """Test search endpoint against SQL injection in query parameter"""
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; INSERT INTO zip_county VALUES ('hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked', 'hacked'); --",
            "'; DELETE FROM zip_county; --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/search?q={payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_location_search_sql_injection(self):
        """Test location search endpoint against SQL injection"""
        injection_payloads = [
            "'; DROP TABLE zip_county; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM sqlite_master --",
            "'; DELETE FROM zip_county; --"
        ]
        
        for payload in injection_payloads:
            response = requests.get(f"{self.api_base}/location/search?q={payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"SQL injection successful with payload: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")
    
    def test_database_integrity_after_injection_attempts(self):
        """Test that database remains intact after injection attempts"""
        # Record initial state
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Count tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        initial_tables = set(row[0] for row in cursor.fetchall())
        
        # Count rows in main tables
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        initial_zip_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        initial_health_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Perform various injection attempts
        injection_tests = [
            f"{self.api_base}/county_data?state='; DROP TABLE zip_county; --",
            f"{self.api_base}/county_data?limit=1; DROP TABLE county_health_rankings; --",
            f"{self.api_base}/search?q='; DELETE FROM zip_county; --",
            f"{self.api_base}/health_rankings?county='; DROP TABLE zip_county; --",
            f"{self.api_base}/zip/'; DROP TABLE zip_county; --"
        ]
        
        for test_url in injection_tests:
            try:
                response = requests.get(test_url)
                # Should not crash the application
                assert response.status_code in [200, 400, 404], f"Unexpected status for {test_url}"
            except requests.exceptions.RequestException:
                # Connection errors are acceptable (app might be down)
                pass
        
        # Verify database integrity
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check tables still exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        current_tables = set(row[0] for row in cursor.fetchall())
        assert current_tables == initial_tables, "Tables were dropped or created"
        
        # Check row counts
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        current_zip_count = cursor.fetchone()[0]
        assert current_zip_count == initial_zip_count, "ZIP county data was modified"
        
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        current_health_count = cursor.fetchone()[0]
        assert current_health_count == initial_health_count, "Health rankings data was modified"
        
        conn.close()
    
    def test_blind_sql_injection_attempts(self):
        """Test for blind SQL injection vulnerabilities"""
        # Test boolean-based blind SQL injection
        true_conditions = [
            "1=1",
            "1=1 OR 1=1",
            "'1'='1'",
            "1 AND 1=1"
        ]
        
        false_conditions = [
            "1=0",
            "1=0 AND 1=1",
            "'1'='0'",
            "1 AND 1=0"
        ]
        
        for condition in true_conditions:
            response = requests.get(f"{self.api_base}/county_data?state=' OR {condition} --")
            # Should not return different results based on condition
            assert response.status_code in [200, 400, 404]
        
        for condition in false_conditions:
            response = requests.get(f"{self.api_base}/county_data?state=' OR {condition} --")
            # Should not return different results based on condition
            assert response.status_code in [200, 400, 404]
    
    def test_time_based_sql_injection(self):
        """Test for time-based blind SQL injection vulnerabilities"""
        import time
        
        # Test with time-based payloads
        time_payloads = [
            "'; WAITFOR DELAY '00:00:05'; --",  # SQL Server
            "'; SELECT SLEEP(5); --",  # MySQL
            "'; SELECT pg_sleep(5); --",  # PostgreSQL
        ]
        
        for payload in time_payloads:
            start_time = time.time()
            response = requests.get(f"{self.api_base}/county_data?state={payload}")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response should not be delayed by 5 seconds (indicates time-based injection)
            assert response_time < 3.0, f"Possible time-based SQL injection with payload: {payload}"
    
    def test_union_based_sql_injection(self):
        """Test for union-based SQL injection vulnerabilities"""
        union_payloads = [
            "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14 --",
            "' UNION SELECT * FROM sqlite_master --",
            "' UNION SELECT name,type FROM sqlite_master --",
            "' UNION SELECT sql FROM sqlite_master --"
        ]
        
        for payload in union_payloads:
            response = requests.get(f"{self.api_base}/county_data?state={payload}")
            
            # Should not return 500 error
            assert response.status_code != 500, f"Union-based SQL injection successful: {payload}"
            
            # Should return valid JSON
            try:
                data = response.json()
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response for payload: {payload}")


if __name__ == "__main__":
    pytest.main([__file__])
