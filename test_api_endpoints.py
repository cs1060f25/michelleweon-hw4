#!/usr/bin/env python3
"""
Test suite for API endpoints
Tests all API endpoints with various scenarios and edge cases
"""

import pytest
import requests
import json
import time
import os
import sqlite3
from unittest.mock import patch


class TestAPIEndpoints:
    """Test cases for all API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.base_url = "http://localhost:5002"  # Adjust port as needed
        self.api_base = f"{self.base_url}/api"
        self.test_db_path = "data.db"
        
        # Ensure database exists and is populated
        if not os.path.exists(self.test_db_path):
            pytest.skip("Database not found. Run csv_to_sqlite.py first.")
    
    def test_root_endpoint(self):
        """Test the root endpoint returns HTML page"""
        response = requests.get(self.base_url)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_county_data_endpoint_basic(self):
        """Test basic county data endpoint functionality"""
        response = requests.get(f"{self.api_base}/county_data")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Check data structure
        if data["data"]:
            county = data["data"][0]
            required_fields = ["county", "state", "default_city", "zip_count"]
            for field in required_fields:
                assert field in county
    
    def test_county_data_with_state_filter(self):
        """Test county data endpoint with state filter"""
        response = requests.get(f"{self.api_base}/county_data?state=CA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # Verify all returned counties are from California
        for county in data["data"]:
            assert county["state"] == "CA"
    
    def test_county_data_with_limit(self):
        """Test county data endpoint with limit parameter"""
        response = requests.get(f"{self.api_base}/county_data?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) <= 5
    
    def test_county_data_invalid_state(self):
        """Test county data endpoint with invalid state"""
        response = requests.get(f"{self.api_base}/county_data?state=INVALID")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []
    
    def test_county_details_endpoint(self):
        """Test county details endpoint"""
        # First get a list of counties to test with
        response = requests.get(f"{self.api_base}/county_data?limit=1")
        assert response.status_code == 200
        
        counties = response.json()["data"]
        if not counties:
            pytest.skip("No counties available for testing")
        
        county_name = counties[0]["county"]
        response = requests.get(f"{self.api_base}/county_data/{county_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        county_data = data["data"]
        required_fields = ["county", "state", "default_city", "zip_count", "zip_codes"]
        for field in required_fields:
            assert field in county_data
    
    def test_county_details_with_state(self):
        """Test county details endpoint with state parameter"""
        # Get a county from a specific state
        response = requests.get(f"{self.api_base}/county_data?state=CA&limit=1")
        assert response.status_code == 200
        
        counties = response.json()["data"]
        if not counties:
            pytest.skip("No California counties available for testing")
        
        county_name = counties[0]["county"]
        response = requests.get(f"{self.api_base}/county_data/{county_name}?state=CA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["state"] == "CA"
    
    def test_county_details_not_found(self):
        """Test county details endpoint with non-existent county"""
        response = requests.get(f"{self.api_base}/county_data/NonExistentCounty")
        assert response.status_code == 404
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_zip_info_endpoint(self):
        """Test ZIP code info endpoint"""
        # First get a ZIP code from the database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT col__zip FROM zip_county LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            pytest.skip("No ZIP codes available for testing")
        
        zip_code = result[0]
        response = requests.get(f"{self.api_base}/zip/{zip_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        zip_data = data["data"]
        required_fields = ["zip_code", "county", "state", "default_city", "health_rankings"]
        for field in required_fields:
            assert field in zip_data
    
    def test_zip_info_not_found(self):
        """Test ZIP code info endpoint with non-existent ZIP"""
        response = requests.get(f"{self.api_base}/zip/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_health_rankings_endpoint(self):
        """Test health rankings endpoint"""
        response = requests.get(f"{self.api_base}/health_rankings")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert "data" in data
        
        # Check pagination
        assert data["page"] == 1
        assert data["per_page"] == 20
        assert data["total"] >= data["count"]
    
    def test_health_rankings_with_pagination(self):
        """Test health rankings endpoint with pagination"""
        response = requests.get(f"{self.api_base}/health_rankings?page=2&per_page=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["page"] == 2
        assert data["per_page"] == 5
        assert len(data["data"]) <= 5
    
    def test_health_rankings_with_filters(self):
        """Test health rankings endpoint with county and state filters"""
        response = requests.get(f"{self.api_base}/health_rankings?county=Los Angeles&state=CA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # Verify all results match the filter
        for ranking in data["data"]:
            assert ranking["county"] == "Los Angeles"
            assert ranking["state"] == "CA"
    
    def test_health_rankings_per_page_limit(self):
        """Test health rankings endpoint respects per_page limit"""
        response = requests.get(f"{self.api_base}/health_rankings?per_page=100")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["per_page"] <= 50  # Should be capped at 50
    
    def test_county_health_details_endpoint(self):
        """Test county health details endpoint"""
        # Get a county from the database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT County, State FROM county_health_rankings WHERE County LIKE '%County%' LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            pytest.skip("No county health data available for testing")
        
        county, state = result
        response = requests.get(f"{self.api_base}/health_rankings/{county}/{state}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        health_data = data["data"]
        required_fields = ["county", "state", "health_score", "health_measures"]
        for field in required_fields:
            assert field in health_data
    
    def test_county_health_details_not_found(self):
        """Test county health details endpoint with non-existent county"""
        response = requests.get(f"{self.api_base}/health_rankings/NonExistentCounty/XX")
        assert response.status_code == 200  # Should return empty data, not error
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["health_score"] == 0
        assert data["data"]["health_measures"] == []
    
    def test_search_endpoint(self):
        """Test search endpoint"""
        response = requests.get(f"{self.api_base}/search?q=Los Angeles")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "query" in data
        assert "count" in data
        assert "data" in data
        assert data["query"] == "Los Angeles"
    
    def test_search_endpoint_empty_query(self):
        """Test search endpoint with empty query"""
        response = requests.get(f"{self.api_base}/search?q=")
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_search_endpoint_missing_query(self):
        """Test search endpoint without query parameter"""
        response = requests.get(f"{self.api_base}/search")
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = requests.get(f"{self.api_base}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        stats = data["data"]
        required_fields = ["total_zip_codes", "total_counties", "total_states", "total_health_records", "state_distribution"]
        for field in required_fields:
            assert field in stats
        
        # Verify stats are reasonable
        assert stats["total_zip_codes"] > 0
        assert stats["total_counties"] > 0
        assert stats["total_states"] > 0
        assert isinstance(stats["state_distribution"], list)
    
    def test_location_zip_endpoint(self):
        """Test location ZIP endpoint"""
        # Get a ZIP code from the database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT col__zip FROM zip_county LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            pytest.skip("No ZIP codes available for testing")
        
        zip_code = result[0]
        response = requests.get(f"{self.api_base}/location/zip/{zip_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        location_data = data["data"]
        required_fields = ["zip_code", "location", "statistics", "health_rankings", "county_zips", "city_zips"]
        for field in required_fields:
            assert field in location_data
    
    def test_location_cities_endpoint(self):
        """Test location cities endpoint"""
        response = requests.get(f"{self.api_base}/location/cities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "data" in data
        
        if data["data"]:
            city = data["data"][0]
            required_fields = ["city", "county_count", "state_count", "zip_count", "states"]
            for field in required_fields:
                assert field in city
    
    def test_location_cities_with_filters(self):
        """Test location cities endpoint with state filter and limit"""
        response = requests.get(f"{self.api_base}/location/cities?state=CA&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) <= 5
        
        # Verify all cities are from California
        for city in data["data"]:
            assert "CA" in city["states"]
    
    def test_location_states_endpoint(self):
        """Test location states endpoint"""
        response = requests.get(f"{self.api_base}/location/states")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "data" in data
        
        if data["data"]:
            state = data["data"][0]
            required_fields = ["state", "county_count", "city_count", "zip_count"]
            for field in required_fields:
                assert field in state
    
    def test_location_states_with_limit(self):
        """Test location states endpoint with limit"""
        response = requests.get(f"{self.api_base}/location/states?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) <= 3
    
    def test_location_state_details_endpoint(self):
        """Test location state details endpoint"""
        response = requests.get(f"{self.api_base}/location/states/CA")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        state_data = data["data"]
        required_fields = ["state", "statistics", "counties", "metro_areas", "health_rankings"]
        for field in required_fields:
            assert field in state_data
        
        assert state_data["state"] == "CA"
    
    def test_location_state_details_not_found(self):
        """Test location state details endpoint with non-existent state"""
        response = requests.get(f"{self.api_base}/location/states/XX")
        assert response.status_code == 404
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_location_search_endpoint(self):
        """Test location search endpoint"""
        response = requests.get(f"{self.api_base}/location/search?q=Los Angeles")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "query" in data
        assert "type" in data
        assert "count" in data
        assert "data" in data
    
    def test_location_search_with_type_filter(self):
        """Test location search endpoint with type filter"""
        response = requests.get(f"{self.api_base}/location/search?q=CA&type=state")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["type"] == "state"
        
        # Verify all results are states
        for result in data["data"]:
            assert result["type"] == "state"
    
    def test_location_search_empty_query(self):
        """Test location search endpoint with empty query"""
        response = requests.get(f"{self.api_base}/location/search?q=")
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_location_analytics_endpoint(self):
        """Test location analytics endpoint"""
        response = requests.get(f"{self.api_base}/location/analytics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        analytics = data["data"]
        required_fields = ["geographic_distribution", "top_cities", "health_by_state"]
        for field in required_fields:
            assert field in analytics
            assert isinstance(analytics[field], list)
    
    def test_api_error_handling(self):
        """Test API error handling for malformed requests"""
        # Test with invalid JSON in request body (if applicable)
        response = requests.get(f"{self.api_base}/county_data", 
                              headers={"Content-Type": "application/json"})
        # Should still work as it's a GET request
        assert response.status_code == 200
    
    def test_api_response_headers(self):
        """Test API response headers"""
        response = requests.get(f"{self.api_base}/county_data")
        assert response.status_code == 200
        
        # Check content type
        assert "application/json" in response.headers.get("content-type", "")
        
        # Check that response is not too large (performance test)
        assert len(response.content) < 1024 * 1024  # Less than 1MB
    
    def test_api_response_time(self):
        """Test API response time"""
        start_time = time.time()
        response = requests.get(f"{self.api_base}/county_data")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Response should be reasonably fast (less than 5 seconds)
        assert response_time < 5.0, f"Response time too slow: {response_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])
