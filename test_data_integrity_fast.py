#!/usr/bin/env python3
"""
Fast Data Integrity Tests
Optimized version that runs quickly for development
"""

import pytest
import sqlite3
import os
import csv
from pathlib import Path


class TestDataIntegrityFast:
    """Fast test cases for database structure and data integrity"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.test_db_path = "data.db"
        self.health_csv = "county_health_rankings.csv"
        self.zip_csv = "zip_county.csv"
        
        # Ensure database exists
        if not os.path.exists(self.test_db_path):
            pytest.skip("Database not found. Run csv_to_sqlite.py first.")
    
    def test_database_exists(self):
        """Test that database file exists and is accessible"""
        assert os.path.exists(self.test_db_path), "Database file does not exist"
        assert os.access(self.test_db_path, os.R_OK), "Database file is not readable"
        assert os.access(self.test_db_path, os.W_OK), "Database file is not writable"
    
    def test_database_connection(self):
        """Test that database can be connected to"""
        conn = sqlite3.connect(self.test_db_path)
        assert conn is not None
        conn.close()
    
    def test_required_tables_exist(self):
        """Test that required tables exist in the database"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for required tables
        required_tables = ["county_health_rankings", "zip_county"]
        for table in required_tables:
            assert table in tables, f"Required table '{table}' not found in database"
        
        conn.close()
    
    def test_health_rankings_table_structure(self):
        """Test county_health_rankings table structure"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(county_health_rankings)")
        columns = cursor.fetchall()
        
        # Expected columns from CSV header
        expected_columns = [
            'State', 'County', 'State_code', 'County_code', 'Year_span',
            'Measure_name', 'Measure_id', 'Numerator', 'Denominator',
            'Raw_value', 'Confidence_Interval_Lower_Bound',
            'Confidence_Interval_Upper_Bound', 'Data_Release_Year', 'fipscode'
        ]
        
        actual_columns = [col[1] for col in columns]
        assert len(actual_columns) == len(expected_columns), f"Column count mismatch. Expected {len(expected_columns)}, got {len(actual_columns)}"
        
        for expected_col in expected_columns:
            assert expected_col in actual_columns, f"Expected column '{expected_col}' not found"
        
        # All columns should be TEXT type
        for col in columns:
            assert col[2] == 'TEXT', f"Column '{col[1]}' should be TEXT type, got {col[2]}"
        
        conn.close()
    
    def test_zip_county_table_structure(self):
        """Test zip_county table structure"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(zip_county)")
        columns = cursor.fetchall()
        
        # Expected columns from CSV header (after csv_to_sqlite.py processing)
        expected_columns = [
            'col__zip', 'default_state', 'county', 'county_state', 
            'state_abbreviation', 'county_code', 'zip_pop', 
            'zip_pop_in_county', 'n_counties', 'default_city'
        ]
        
        actual_columns = [col[1] for col in columns]
        assert len(actual_columns) == len(expected_columns), f"Column count mismatch. Expected {len(expected_columns)}, got {len(actual_columns)}"
        
        for expected_col in expected_columns:
            assert expected_col in actual_columns, f"Expected column '{expected_col}' not found"
        
        # All columns should be TEXT type
        for col in columns:
            assert col[2] == 'TEXT', f"Column '{col[1]}' should be TEXT type, got {col[2]}"
        
        conn.close()
    
    def test_health_rankings_data_count(self):
        """Test that health rankings data was properly loaded"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Count rows in health rankings table
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        row_count = cursor.fetchone()[0]
        
        # Should have data
        assert row_count > 0, "No data in county_health_rankings table"
        
        # Just check it's reasonable (not exact match for speed)
        assert row_count > 100000, f"Too few health records: {row_count}"
        
        conn.close()
    
    def test_zip_county_data_count(self):
        """Test that zip county data was properly loaded"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Count rows in zip county table
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        row_count = cursor.fetchone()[0]
        
        # Should have data
        assert row_count > 0, "No data in zip_county table"
        
        # Just check it's reasonable (not exact match for speed)
        assert row_count > 50000, f"Too few ZIP records: {row_count}"
        
        conn.close()
    
    def test_health_rankings_data_quality_basic(self):
        """Test basic health rankings data quality (fast version)"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check for required fields (sample only)
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings WHERE State IS NULL OR State = '' LIMIT 1000")
        null_states = cursor.fetchone()[0]
        # Allow some nulls but not too many
        assert null_states < 100, f"Too many null states in sample: {null_states}"
        
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings WHERE County IS NULL OR County = '' LIMIT 1000")
        null_counties = cursor.fetchone()[0]
        assert null_counties < 100, f"Too many null counties in sample: {null_counties}"
        
        # Check for data consistency (sample)
        cursor.execute("SELECT COUNT(DISTINCT State) FROM county_health_rankings LIMIT 1000")
        states = cursor.fetchone()[0]
        assert states > 0, "No state data found in sample"
        
        conn.close()
    
    def test_zip_county_data_quality_basic(self):
        """Test basic zip county data quality (fast version)"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check for required fields (sample only)
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE col__zip IS NULL OR col__zip = '' LIMIT 1000")
        null_zips = cursor.fetchone()[0]
        assert null_zips < 100, f"Too many null ZIPs in sample: {null_zips}"
        
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE county IS NULL OR county = '' LIMIT 1000")
        null_counties = cursor.fetchone()[0]
        assert null_counties < 100, f"Too many null counties in sample: {null_counties}"
        
        # Check for data consistency (sample)
        cursor.execute("SELECT COUNT(DISTINCT state_abbreviation) FROM zip_county LIMIT 1000")
        state_count = cursor.fetchone()[0]
        assert state_count > 0, "No state data found in sample"
        
        conn.close()
    
    def test_database_performance_basic(self):
        """Test basic database performance (fast version)"""
        import time
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test basic query performance (with LIMIT for speed)
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings LIMIT 1000")
        cursor.fetchone()
        health_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM zip_county LIMIT 1000")
        cursor.fetchone()
        zip_time = time.time() - start_time
        
        # Queries should be fast
        assert health_time < 0.5, f"Health rankings query too slow: {health_time:.2f}s"
        assert zip_time < 0.5, f"ZIP county query too slow: {zip_time:.2f}s"
        
        conn.close()
    
    def test_data_completeness_basic(self):
        """Test that data is reasonably complete (fast version)"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check health rankings completeness (sample)
        cursor.execute("SELECT COUNT(DISTINCT County) FROM county_health_rankings WHERE County LIKE '%County%' LIMIT 1000")
        county_count = cursor.fetchone()[0]
        assert county_count > 100, f"Too few counties in health data sample: {county_count}"
        
        # Check ZIP county completeness (sample)
        cursor.execute("SELECT COUNT(DISTINCT col__zip) FROM zip_county LIMIT 1000")
        zip_count = cursor.fetchone()[0]
        assert zip_count > 100, f"Too few ZIP codes in sample: {zip_count}"
        
        # Check state coverage (sample)
        cursor.execute("SELECT COUNT(DISTINCT state_abbreviation) FROM zip_county LIMIT 1000")
        state_count = cursor.fetchone()[0]
        assert state_count >= 10, f"Too few states in sample: {state_count}"
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__])
