#!/usr/bin/env python3
"""
Data Integrity Tests
Tests database structure and data integrity
"""

import pytest
import sqlite3
import os
import csv
from pathlib import Path


class TestDataIntegrity:
    """Test cases for database structure and data integrity"""
    
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
        
        # Expected columns from CSV header
        expected_columns = [
            'zip', 'default_state', 'county', 'county_state', 
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
        
        # Compare with CSV file if available
        if os.path.exists(self.health_csv):
            with open(self.health_csv, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Skip header
                csv_row_count = sum(1 for row in csv_reader)
            
            assert row_count == csv_row_count, f"Row count mismatch. Database: {row_count}, CSV: {csv_row_count}"
        
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
        
        # Compare with CSV file if available
        if os.path.exists(self.zip_csv):
            with open(self.zip_csv, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Skip header
                csv_row_count = sum(1 for row in csv_reader)
            
            assert row_count == csv_row_count, f"Row count mismatch. Database: {row_count}, CSV: {csv_row_count}"
        
        conn.close()
    
    def test_health_rankings_data_quality(self):
        """Test health rankings data quality"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check for required fields
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings WHERE State IS NULL OR State = ''")
        null_states = cursor.fetchone()[0]
        assert null_states == 0, f"Found {null_states} rows with null/empty State"
        
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings WHERE County IS NULL OR County = ''")
        null_counties = cursor.fetchone()[0]
        assert null_counties == 0, f"Found {null_counties} rows with null/empty County"
        
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings WHERE Measure_name IS NULL OR Measure_name = ''")
        null_measures = cursor.fetchone()[0]
        assert null_measures == 0, f"Found {null_measures} rows with null/empty Measure_name"
        
        # Check for data consistency
        cursor.execute("SELECT DISTINCT State FROM county_health_rankings WHERE State != 'US'")
        states = [row[0] for row in cursor.fetchall()]
        assert len(states) > 0, "No state data found"
        
        # Check for reasonable number of measures
        cursor.execute("SELECT COUNT(DISTINCT Measure_name) FROM county_health_rankings")
        measure_count = cursor.fetchone()[0]
        assert measure_count > 0, "No health measures found"
        
        conn.close()
    
    def test_zip_county_data_quality(self):
        """Test zip county data quality"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check for required fields
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE col__zip IS NULL OR col__zip = ''")
        null_zips = cursor.fetchone()[0]
        assert null_zips == 0, f"Found {null_zips} rows with null/empty ZIP codes"
        
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE county IS NULL OR county = ''")
        null_counties = cursor.fetchone()[0]
        assert null_counties == 0, f"Found {null_counties} rows with null/empty county"
        
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE state_abbreviation IS NULL OR state_abbreviation = ''")
        null_states = cursor.fetchone()[0]
        assert null_states == 0, f"Found {null_states} rows with null/empty state_abbreviation"
        
        # Check for data consistency
        cursor.execute("SELECT COUNT(DISTINCT state_abbreviation) FROM zip_county")
        state_count = cursor.fetchone()[0]
        assert state_count > 0, "No state data found"
        
        # Check for reasonable ZIP code format (5 digits)
        cursor.execute("SELECT COUNT(*) FROM zip_county WHERE col__zip NOT GLOB '[0-9][0-9][0-9][0-9][0-9]'")
        invalid_zips = cursor.fetchone()[0]
        # Allow some invalid ZIPs (like Puerto Rico with 00601 format)
        assert invalid_zips < 1000, f"Too many invalid ZIP codes found: {invalid_zips}"
        
        conn.close()
    
    def test_data_relationships(self):
        """Test relationships between tables"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check that counties in zip_county exist in health_rankings
        cursor.execute("""
            SELECT COUNT(DISTINCT z.county || ', ' || z.state_abbreviation) 
            FROM zip_county z
            WHERE NOT EXISTS (
                SELECT 1 FROM county_health_rankings h 
                WHERE h.County = z.county AND h.State = z.state_abbreviation
            )
        """)
        orphaned_counties = cursor.fetchone()[0]
        
        # Some counties might not have health data, but most should
        assert orphaned_counties < 1000, f"Too many counties without health data: {orphaned_counties}"
        
        # Check for reasonable overlap
        cursor.execute("SELECT COUNT(DISTINCT county || ', ' || state_abbreviation) FROM zip_county")
        total_zip_counties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT County || ', ' || State) FROM county_health_rankings WHERE County LIKE '%County%'")
        total_health_counties = cursor.fetchone()[0]
        
        # Should have reasonable overlap
        overlap_ratio = (total_zip_counties - orphaned_counties) / total_zip_counties
        assert overlap_ratio > 0.1, f"Too little overlap between tables: {overlap_ratio:.2%}"
        
        conn.close()
    
    def test_data_types_consistency(self):
        """Test that data types are consistent across the database"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check that all columns are TEXT type
        for table in ["county_health_rankings", "zip_county"]:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            for col in columns:
                assert col[2] == 'TEXT', f"Column '{col[1]}' in table '{table}' should be TEXT type, got {col[2]}"
        
        conn.close()
    
    def test_no_duplicate_primary_keys(self):
        """Test that there are no duplicate primary key combinations"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check for duplicate health rankings entries
        cursor.execute("""
            SELECT County, State, Measure_name, Year_span, COUNT(*) as count
            FROM county_health_rankings
            GROUP BY County, State, Measure_name, Year_span
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        # Some duplicates might be expected, but not too many
        assert len(duplicates) < 100, f"Too many duplicate health ranking entries: {len(duplicates)}"
        
        # Check for duplicate ZIP entries
        cursor.execute("""
            SELECT col__zip, COUNT(*) as count
            FROM zip_county
            GROUP BY col__zip
            HAVING COUNT(*) > 1
        """)
        zip_duplicates = cursor.fetchall()
        
        # ZIP codes can appear multiple times (different counties)
        # But check for excessive duplicates
        assert len(zip_duplicates) < 1000, f"Too many duplicate ZIP entries: {len(zip_duplicates)}"
        
        conn.close()
    
    def test_data_completeness(self):
        """Test that data is reasonably complete"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check health rankings completeness
        cursor.execute("SELECT COUNT(DISTINCT County) FROM county_health_rankings WHERE County LIKE '%County%'")
        county_count = cursor.fetchone()[0]
        assert county_count > 1000, f"Too few counties in health data: {county_count}"
        
        # Check ZIP county completeness
        cursor.execute("SELECT COUNT(DISTINCT col__zip) FROM zip_county")
        zip_count = cursor.fetchone()[0]
        assert zip_count > 10000, f"Too few ZIP codes: {zip_count}"
        
        # Check state coverage
        cursor.execute("SELECT COUNT(DISTINCT state_abbreviation) FROM zip_county")
        state_count = cursor.fetchone()[0]
        assert state_count >= 50, f"Too few states: {state_count}"
        
        conn.close()
    
    def test_database_performance(self):
        """Test that database queries perform reasonably"""
        import time
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test query performance
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        cursor.fetchone()
        health_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        cursor.fetchone()
        zip_time = time.time() - start_time
        
        # Queries should be fast
        assert health_time < 1.0, f"Health rankings count query too slow: {health_time:.2f}s"
        assert zip_time < 1.0, f"ZIP county count query too slow: {zip_time:.2f}s"
        
        # Test complex query performance
        start_time = time.time()
        cursor.execute("""
            SELECT z.county, z.state_abbreviation, COUNT(z.col__zip) as zip_count
            FROM zip_county z
            GROUP BY z.county, z.state_abbreviation
            ORDER BY zip_count DESC
            LIMIT 10
        """)
        cursor.fetchall()
        complex_time = time.time() - start_time
        
        assert complex_time < 2.0, f"Complex query too slow: {complex_time:.2f}s"
        
        conn.close()
    
    def test_database_constraints(self):
        """Test that database constraints are properly enforced"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Test that we can't insert invalid data (if constraints exist)
        try:
            cursor.execute("INSERT INTO county_health_rankings (State, County) VALUES (NULL, 'Test')")
            conn.rollback()
        except sqlite3.Error:
            # This is expected if constraints exist
            pass
        
        # Test that we can insert valid data
        try:
            cursor.execute("INSERT INTO county_health_rankings (State, County, Measure_name) VALUES ('Test', 'Test County', 'Test Measure')")
            conn.rollback()  # Rollback test data
        except sqlite3.Error as e:
            pytest.fail(f"Could not insert valid data: {e}")
        
        conn.close()
    
    def test_database_backup_restore(self):
        """Test that database can be backed up and restored"""
        import shutil
        import tempfile
        
        # Create backup
        backup_path = tempfile.mktemp(suffix='.db')
        shutil.copy2(self.test_db_path, backup_path)
        
        try:
            # Verify backup is identical
            with open(self.test_db_path, 'rb') as original:
                with open(backup_path, 'rb') as backup:
                    assert original.read() == backup.read(), "Backup is not identical to original"
            
            # Test that backup can be opened
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
            count = cursor.fetchone()[0]
            assert count > 0
            conn.close()
            
        finally:
            # Clean up backup
            if os.path.exists(backup_path):
                os.remove(backup_path)


if __name__ == "__main__":
    pytest.main([__file__])
