#!/usr/bin/env python3
"""
Setup Validation Script
Validates that the test environment is properly configured
"""

import os
import sys
import subprocess
import sqlite3
import requests
import time


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required, found:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def check_required_files():
    """Check required files exist"""
    print("\nChecking required files...")
    required_files = [
        "csv_to_sqlite.py",
        "api/index.py",
        "county_health_rankings.csv",
        "zip_county.csv",
        "data.db"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            all_exist = False
    
    return all_exist


def check_database():
    """Check database structure and data"""
    print("\nChecking database...")
    
    if not os.path.exists("data.db"):
        print("❌ Database not found. Run csv_to_sqlite.py first.")
        return False
    
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ["county_health_rankings", "zip_county"]
        for table in required_tables:
            if table in tables:
                print(f"✅ Table {table} - Found")
            else:
                print(f"❌ Table {table} - Missing")
                return False
        
        # Check data exists
        cursor.execute("SELECT COUNT(*) FROM county_health_rankings")
        health_count = cursor.fetchone()[0]
        print(f"✅ Health rankings data - {health_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM zip_county")
        zip_count = cursor.fetchone()[0]
        print(f"✅ ZIP county data - {zip_count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def check_test_dependencies():
    """Check test dependencies are installed"""
    print("\nChecking test dependencies...")
    
    try:
        import pytest
        print("✅ pytest - Installed")
    except ImportError:
        print("❌ pytest - Missing")
        return False
    
    try:
        import requests
        print("✅ requests - Installed")
    except ImportError:
        print("❌ requests - Missing")
        return False
    
    try:
        import psutil
        print("✅ psutil - Installed")
    except ImportError:
        print("❌ psutil - Missing")
        return False
    
    return True


def check_api_running():
    """Check if API is running"""
    print("\nChecking API status...")
    
    try:
        response = requests.get("http://localhost:5002", timeout=5)
        if response.status_code == 200:
            print("✅ API is running on localhost:5002")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start with: python api/index.py")
        return False
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return False


def run_sample_tests():
    """Run a few sample tests to verify everything works"""
    print("\nRunning sample tests...")
    
    # Test CSV converter
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_csv_converter.py::TestCSVConverter::test_converter_with_arbitrary_csv", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ CSV converter test - Passed")
        else:
            print("❌ CSV converter test - Failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ CSV converter test error: {e}")
        return False
    
    # Test data integrity
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_data_integrity.py::TestDataIntegrity::test_database_exists", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Data integrity test - Passed")
        else:
            print("❌ Data integrity test - Failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Data integrity test error: {e}")
        return False
    
    return True


def main():
    """Main validation function"""
    print("API Assignment Test Environment Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Database", check_database),
        ("Test Dependencies", check_test_dependencies),
        ("API Status", check_api_running),
        ("Sample Tests", run_sample_tests)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Test environment is ready.")
        print("\nYou can now run:")
        print("  python run_tests.py        # Run all tests")
        print("  python run_tests.py csv    # Run CSV tests only")
        print("  python run_tests.py api    # Run API tests only")
    else:
        print("❌ SOME CHECKS FAILED! Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r test_requirements.txt")
        print("  2. Populate database: python csv_to_sqlite.py data.db county_health_rankings.csv")
        print("  3. Start API: python api/index.py")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
