#!/usr/bin/env python3
"""
Test Runner for API Assignment
Runs all test suites and generates comprehensive reports
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status and output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        
        print(f"Exit code: {result.returncode}")
        print(f"Duration: {end_time - start_time:.2f} seconds")
        
        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("Command timed out after 5 minutes")
        return False, "", "Timeout"
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)


def check_prerequisites():
    """Check that all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required")
        return False
    
    # Check required files
    required_files = [
        "csv_to_sqlite.py",
        "api/index.py",
        "county_health_rankings.csv",
        "zip_county.csv"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"ERROR: Required file not found: {file}")
            return False
    
    # Check test data directory
    if not os.path.exists("test_data"):
        print("ERROR: Test data directory not found")
        return False
    
    print("All prerequisites met!")
    return True


def install_test_dependencies():
    """Install test dependencies"""
    print("\nInstalling test dependencies...")
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"
    ], "Installing test dependencies")
    
    if not success:
        print("WARNING: Failed to install some test dependencies")
        print("Some tests may fail")
    
    return success


def run_csv_converter_tests():
    """Run CSV converter tests"""
    print("\n" + "="*80)
    print("RUNNING CSV CONVERTER TESTS")
    print("="*80)
    
    # Test with original data
    success1, stdout1, stderr1 = run_command([
        sys.executable, "-m", "pytest", "test_csv_converter.py", "-v", "--tb=short"
    ], "CSV Converter Tests")
    
    return success1


def run_api_tests():
    """Run API endpoint tests"""
    print("\n" + "="*80)
    print("RUNNING API ENDPOINT TESTS")
    print("="*80)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        api_running = True
    except:
        api_running = False
        print("WARNING: API is not running on localhost:5001")
        print("Please start the API with: python api/index.py")
        print("Skipping API tests...")
        return False
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", "test_api_endpoints.py", "-v", "--tb=short"
    ], "API Endpoint Tests")
    
    return success


def run_security_tests():
    """Run SQL injection security tests"""
    print("\n" + "="*80)
    print("RUNNING SECURITY TESTS")
    print("="*80)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        api_running = True
    except:
        api_running = False
        print("WARNING: API is not running on localhost:5001")
        print("Please start the API with: python api/index.py")
        print("Skipping security tests...")
        return False
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", "test_sql_injection.py", "-v", "--tb=short"
    ], "SQL Injection Security Tests")
    
    return success


def run_data_integrity_tests():
    """Run data integrity tests"""
    print("\n" + "="*80)
    print("RUNNING DATA INTEGRITY TESTS")
    print("="*80)
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", "test_data_integrity.py", "-v", "--tb=short"
    ], "Data Integrity Tests")
    
    return success


def run_performance_tests():
    """Run performance tests"""
    print("\n" + "="*80)
    print("RUNNING PERFORMANCE TESTS")
    print("="*80)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://localhost:5001", timeout=5)
        api_running = True
    except:
        api_running = False
        print("WARNING: API is not running on localhost:5001")
        print("Please start the API with: python api/index.py")
        print("Skipping performance tests...")
        return False
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", "test_performance.py", "-v", "--tb=short"
    ], "Performance Tests")
    
    return success


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("RUNNING ALL TESTS")
    print("="*80)
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", 
        "test_csv_converter.py",
        "test_api_endpoints.py", 
        "test_sql_injection.py",
        "test_data_integrity.py",
        "test_performance.py",
        "-v", "--tb=short", "--durations=10"
    ], "All Tests")
    
    return success


def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*80)
    print("GENERATING TEST REPORT")
    print("="*80)
    
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pytest", 
        "test_csv_converter.py",
        "test_api_endpoints.py", 
        "test_sql_injection.py",
        "test_data_integrity.py",
        "test_performance.py",
        "--json-report", "--json-report-file=test_report.json",
        "-v"
    ], "Generating JSON Test Report")
    
    if success and os.path.exists("test_report.json"):
        print("Test report generated: test_report.json")
        
        # Also generate HTML report if pytest-html is available
        try:
            success_html, stdout_html, stderr_html = run_command([
                sys.executable, "-m", "pytest", 
                "test_csv_converter.py",
                "test_api_endpoints.py", 
                "test_sql_injection.py",
                "test_data_integrity.py",
                "test_performance.py",
                "--html=test_report.html", "--self-contained-html",
                "-v"
            ], "Generating HTML Test Report")
            
            if success_html:
                print("HTML test report generated: test_report.html")
        except:
            print("HTML report generation skipped (pytest-html not available)")
    
    return success


def main():
    """Main test runner function"""
    print("API Assignment Test Suite")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Exiting.")
        sys.exit(1)
    
    # Install dependencies
    install_test_dependencies()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    # Run tests based on type
    if test_type == "csv":
        success = run_csv_converter_tests()
    elif test_type == "api":
        success = run_api_tests()
    elif test_type == "security":
        success = run_security_tests()
    elif test_type == "data":
        success = run_data_integrity_tests()
    elif test_type == "performance":
        success = run_performance_tests()
    elif test_type == "all":
        success = run_all_tests()
        generate_test_report()
    else:
        print(f"Unknown test type: {test_type}")
        print("Available types: csv, api, security, data, performance, all")
        sys.exit(1)
    
    # Print final results
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("="*80)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
