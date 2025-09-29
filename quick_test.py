#!/usr/bin/env python3
"""
Quick Test Runner - Fast subset of tests for development
"""

import subprocess
import sys
import time


def run_quick_tests():
    """Run a quick subset of the most important tests"""
    print("🚀 Quick Test Suite - Fast Development Testing")
    print("=" * 60)
    
    tests = [
        {
            "name": "CSV Converter (Core)",
            "file": "test_csv_converter.py::TestCSVConverter::test_converter_with_arbitrary_csv",
            "description": "Tests CSV converter with arbitrary data"
        },
        {
            "name": "Data Integrity (Core)",
            "file": "test_data_integrity_fast.py::TestDataIntegrityFast::test_database_exists",
            "description": "Tests database exists and is accessible"
        },
        {
            "name": "API Basic (if running)",
            "file": "test_api_endpoints.py::TestAPIEndpoints::test_root_endpoint",
            "description": "Tests basic API functionality"
        }
    ]
    
    total_start = time.time()
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n🧪 Running: {test['name']}")
        print(f"   {test['description']}")
        
        start_time = time.time()
        result = subprocess.run([
            sys.executable, "-m", "pytest", test['file'], "-v", "--tb=short", "-q"
        ], capture_output=True, text=True, timeout=30)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ PASSED ({duration:.1f}s)")
            passed += 1
        else:
            print(f"   ❌ FAILED ({duration:.1f}s)")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            failed += 1
    
    total_duration = time.time() - total_start
    
    print("\n" + "=" * 60)
    print(f"📊 Quick Test Results: {passed} passed, {failed} failed")
    print(f"⏱️  Total time: {total_duration:.1f} seconds")
    
    if failed == 0:
        print("🎉 All quick tests passed!")
    else:
        print("⚠️  Some tests failed - run full suite for details")
    
    return failed == 0


def run_specific_test(test_name):
    """Run a specific test quickly"""
    test_map = {
        "csv": "test_csv_converter.py",
        "data": "test_data_integrity_fast.py", 
        "data-full": "test_data_integrity.py",
        "api": "test_api_endpoints.py::TestAPIEndpoints::test_root_endpoint",
        "security": "test_sql_injection.py::TestSQLInjection::test_county_data_sql_injection_state",
        "perf": "test_performance.py::TestPerformance::test_api_response_times"
    }
    
    if test_name not in test_map:
        print(f"Unknown test: {test_name}")
        print(f"Available: {', '.join(test_map.keys())}")
        return False
    
    print(f"🧪 Running {test_name} test...")
    start_time = time.time()
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", test_map[test_name], "-v", "--tb=short"
    ], capture_output=True, text=True, timeout=60)
    
    duration = time.time() - start_time
    
    if result.returncode == 0:
        print(f"✅ PASSED ({duration:.1f}s)")
        return True
    else:
        print(f"❌ FAILED ({duration:.1f}s)")
        print(result.stdout)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        success = run_specific_test(test_name)
    else:
        success = run_quick_tests()
    
    sys.exit(0 if success else 1)
