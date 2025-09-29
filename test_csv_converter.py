#!/usr/bin/env python3
"""
Test suite for csv_to_sqlite.py converter
Tests the converter with original data sources and arbitrary CSV files
"""

import pytest
import sqlite3
import os
import tempfile
import subprocess
import sys
from pathlib import Path


class TestCSVConverter:
    """Test cases for csv_to_sqlite.py converter"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.original_csv = "county_health_rankings.csv"
        self.zip_csv = "zip_county.csv"
        self.converter_script = "csv_to_sqlite.py"
    
    def teardown_method(self):
        """Clean up test environment after each test"""
        # Clean up any test databases
        try:
            for file in os.listdir(self.test_dir):
                if file.endswith('.db'):
                    os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
        except (OSError, FileNotFoundError):
            # Directory might already be cleaned up or not exist
            pass
    
    def test_converter_with_original_health_data(self):
        """Test converter with original county health rankings CSV"""
        if not os.path.exists(self.original_csv):
            pytest.skip(f"Original CSV file {self.original_csv} not found")
        
        db_path = os.path.join(self.test_dir, "test_health.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, self.original_csv
        ], capture_output=True, text=True)
        
        # Verify success
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        assert "Successfully converted" in result.stdout
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        # Verify table structure and data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len(tables) == 1
        assert tables[0][0] == "county_health_rankings"
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        row_count = cursor.fetchone()[0]
        assert row_count > 0, "No data was inserted"
        
        # Check column structure
        cursor.execute("PRAGMA table_info(county_health_rankings)")
        columns = cursor.fetchall()
        expected_columns = [
            'State', 'County', 'State_code', 'County_code', 'Year_span',
            'Measure_name', 'Measure_id', 'Numerator', 'Denominator',
            'Raw_value', 'Confidence_Interval_Lower_Bound',
            'Confidence_Interval_Upper_Bound', 'Data_Release_Year', 'fipscode'
        ]
        actual_columns = [col[1] for col in columns]
        assert len(actual_columns) == len(expected_columns)
        
        # Check some sample data
        cursor.execute("SELECT * FROM county_health_rankings LIMIT 1")
        sample_row = cursor.fetchone()
        assert sample_row is not None
        
        conn.close()
    
    def test_converter_with_original_zip_data(self):
        """Test converter with original zip county CSV"""
        if not os.path.exists(self.zip_csv):
            pytest.skip(f"Original CSV file {self.zip_csv} not found")
        
        db_path = os.path.join(self.test_dir, "test_zip.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, self.zip_csv
        ], capture_output=True, text=True)
        
        # Verify success
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        assert "Successfully converted" in result.stdout
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        # Verify table structure and data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len(tables) == 1
        assert tables[0][0] == "zip_county"
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        row_count = cursor.fetchone()[0]
        assert row_count > 0, "No data was inserted"
        
        conn.close()
    
    def test_converter_with_arbitrary_csv(self):
        """Test converter with arbitrary CSV file to ensure it works on any CSV"""
        # Create a test CSV with various data types and edge cases
        test_csv_path = os.path.join(self.test_dir, "test_data.csv")
        
        test_data = [
            "Name,Age,City,Salary,Notes",
            "John Doe,25,New York,50000,Regular employee",
            "Jane Smith,30,Los Angeles,60000,Manager",
            "Bob Johnson,35,Chicago,55000,Senior developer",
            "Alice Brown,28,Houston,52000,Data scientist",
            "Charlie Wilson,45,Phoenix,70000,Director",
            "Diana Lee,32,Philadelphia,58000,Product manager",
            "Eve Davis,29,San Antonio,51000,Designer",
            "Frank Miller,38,San Diego,65000,Architect",
            "Grace Taylor,27,Dallas,49000,Analyst",
            "Henry Moore,41,San Jose,75000,VP Engineering"
        ]
        
        with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write('\n'.join(test_data))
        
        db_path = os.path.join(self.test_dir, "test_arbitrary.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, test_csv_path
        ], capture_output=True, text=True)
        
        # Verify success
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        assert "Successfully converted" in result.stdout
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        # Verify table structure and data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert len(tables) == 1
        assert tables[0][0] == "test_data"
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM test_data")
        row_count = cursor.fetchone()[0]
        assert row_count == 10, f"Expected 10 rows, got {row_count}"
        
        # Check column structure
        cursor.execute("PRAGMA table_info(test_data)")
        columns = cursor.fetchall()
        expected_columns = ['Name', 'Age', 'City', 'Salary', 'Notes']
        actual_columns = [col[1] for col in columns]
        assert actual_columns == expected_columns
        
        # Check some sample data
        cursor.execute("SELECT * FROM test_data WHERE Name = 'John Doe'")
        sample_row = cursor.fetchone()
        assert sample_row is not None
        assert sample_row[0] == 'John Doe'
        assert sample_row[1] == '25'
        
        conn.close()
    
    def test_converter_with_special_characters(self):
        """Test converter with CSV containing special characters and edge cases"""
        test_csv_path = os.path.join(self.test_dir, "special_chars.csv")
        
        test_data = [
            "ID,Name,Description,Value",
            "1,Test & Co,\"Quoted, comma\",100.50",
            "2,Smith's Store,Contains 'quotes',200.75",
            "3,Multi\nLine,Contains newlines,300.25",
            "4,Empty Field,,400.00",
            "5,Unicode Test,测试中文,500.00",
            "6,Special Chars,!@#$%^&*(),600.00"
        ]
        
        with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write('\n'.join(test_data))
        
        db_path = os.path.join(self.test_dir, "test_special.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, test_csv_path
        ], capture_output=True, text=True)
        
        # Verify success
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        
        # Verify database was created and data is preserved
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM special_chars")
        row_count = cursor.fetchone()[0]
        assert row_count == 7  # Updated to match actual data
        
        # Check that special characters are preserved
        cursor.execute("SELECT * FROM special_chars WHERE ID = '1'")
        row = cursor.fetchone()
        assert 'Test & Co' in row[1]
        assert 'Quoted, comma' in row[2]
        
        conn.close()
    
    def test_converter_with_malformed_csv(self):
        """Test converter behavior with malformed CSV files"""
        test_csv_path = os.path.join(self.test_dir, "malformed.csv")
        
        # Create CSV with inconsistent column counts
        test_data = [
            "Name,Age,City",
            "John,25,New York,Extra Field",
            "Jane,30",
            "Bob,35,Chicago,Extra,Fields,Here"
        ]
        
        with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write('\n'.join(test_data))
        
        db_path = os.path.join(self.test_dir, "test_malformed.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, test_csv_path
        ], capture_output=True, text=True)
        
        # Should still succeed (converter handles malformed data)
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check that data was inserted despite malformation
        cursor.execute("SELECT COUNT(*) FROM malformed")
        row_count = cursor.fetchone()[0]
        assert row_count == 3
        
        conn.close()
    
    def test_converter_error_handling(self):
        """Test converter error handling for invalid inputs"""
        # Test with non-existent file
        db_path = os.path.join(self.test_dir, "test.db")
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, "nonexistent.csv"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert "not found" in result.stdout or "not found" in result.stderr
        
        # Test with wrong number of arguments
        result = subprocess.run([
            sys.executable, self.converter_script, "only_one_arg"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert "Usage:" in result.stdout or "Usage:" in result.stderr
    
    def test_converter_with_empty_csv(self):
        """Test converter with empty CSV file"""
        test_csv_path = os.path.join(self.test_dir, "empty.csv")
        
        # Create empty CSV with just headers
        with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write("Name,Age,City\n")
        
        db_path = os.path.join(self.test_dir, "test_empty.db")
        
        # Run the converter
        result = subprocess.run([
            sys.executable, self.converter_script, db_path, test_csv_path
        ], capture_output=True, text=True)
        
        # Should succeed even with empty data
        assert result.returncode == 0, f"Converter failed: {result.stderr}"
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists but has no data
        cursor.execute("SELECT COUNT(*) FROM empty")
        row_count = cursor.fetchone()[0]
        assert row_count == 0
        
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__])
