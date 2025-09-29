# API Assignment Test Suite

This comprehensive test suite is designed to validate your API assignment for CS1060 Homework 4. The tests cover all aspects mentioned in the grading criteria and ensure your code will pass automated testing.

## Test Coverage

### 1. CSV Converter Tests (`test_csv_converter.py`)
- ✅ Tests with original data sources (`county_health_rankings.csv`, `zip_county.csv`)
- ✅ Tests with arbitrary CSV files to ensure general functionality
- ✅ Tests with special characters, malformed data, and edge cases
- ✅ Error handling and validation
- ✅ Data integrity verification

### 2. API Endpoint Tests (`test_api_endpoints.py`)
- ✅ All API endpoints functionality
- ✅ Query parameters and filtering
- ✅ Pagination and limits
- ✅ Error handling (404, 400, 500)
- ✅ Response format validation
- ✅ Edge cases and boundary conditions

### 3. SQL Injection Security Tests (`test_sql_injection.py`)
- ✅ Comprehensive SQL injection attack simulation
- ✅ Parameterized query validation
- ✅ Database integrity after attack attempts
- ✅ Blind SQL injection testing
- ✅ Union-based injection testing
- ✅ Time-based injection testing

### 4. Data Integrity Tests (`test_data_integrity.py`)
- ✅ Database structure validation
- ✅ Data completeness checks
- ✅ Data quality verification
- ✅ Table relationships
- ✅ Performance benchmarks
- ✅ Backup/restore functionality

### 5. Performance Tests (`test_performance.py`)
- ✅ API response time validation
- ✅ Database query performance
- ✅ Concurrent request handling
- ✅ Memory usage monitoring
- ✅ Large response handling
- ✅ Error response performance

## Prerequisites

1. **Python 3.7+** installed
2. **Database populated** - Run `python csv_to_sqlite.py data.db county_health_rankings.csv` and `python csv_to_sqlite.py data.db zip_county.csv`
3. **API running** - Start with `python api/index.py` (for API tests)
4. **Test dependencies** - Install with `pip install -r test_requirements.txt`

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Suites
```bash
# CSV Converter tests only
python run_tests.py csv

# API endpoint tests only
python run_tests.py api

# Security tests only
python run_tests.py security

# Data integrity tests only
python run_tests.py data

# Performance tests only
python run_tests.py performance
```

### Run Individual Test Files
```bash
# CSV converter tests
python -m pytest test_csv_converter.py -v

# API endpoint tests (requires API running)
python -m pytest test_api_endpoints.py -v

# Security tests (requires API running)
python -m pytest test_sql_injection.py -v

# Data integrity tests
python -m pytest test_data_integrity.py -v

# Performance tests (requires API running)
python -m pytest test_performance.py -v
```

## Test Data

The test suite includes sample data in the `test_data/` directory:
- `sample_data.csv` - Standard test data with various data types
- `special_characters.csv` - Data with special characters and edge cases
- `malformed_data.csv` - Intentionally malformed data for error testing
- `empty_data.csv` - Empty data file for boundary testing

## Expected Results

### CSV Converter Tests
- ✅ All original CSV files should convert successfully
- ✅ Arbitrary CSV files should work with proper column handling
- ✅ Special characters should be preserved
- ✅ Malformed data should be handled gracefully
- ✅ Error conditions should be handled properly

### API Endpoint Tests
- ✅ All endpoints should return 200 status for valid requests
- ✅ Error endpoints should return appropriate 4xx/5xx status codes
- ✅ Response format should match expected JSON structure
- ✅ Query parameters should work correctly
- ✅ Pagination should function properly

### Security Tests
- ✅ No SQL injection should be possible
- ✅ Database should remain intact after attack attempts
- ✅ All queries should use parameterized statements
- ✅ No sensitive data should be exposed

### Data Integrity Tests
- ✅ Database structure should match expected schema
- ✅ All data should be properly loaded
- ✅ Data relationships should be consistent
- ✅ No data corruption should occur

### Performance Tests
- ✅ API responses should be under 2-3 seconds
- ✅ Database queries should be under 1-2 seconds
- ✅ Concurrent requests should be handled properly
- ✅ Memory usage should be reasonable

## Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   python csv_to_sqlite.py data.db county_health_rankings.csv
   python csv_to_sqlite.py data.db zip_county.csv
   ```

2. **API not running**
   ```bash
   python api/index.py
   # Keep this running in a separate terminal
   ```

3. **Missing dependencies**
   ```bash
   pip install -r test_requirements.txt
   ```

4. **Permission errors**
   ```bash
   chmod +x run_tests.py
   python run_tests.py
   ```

### Test Failures

If tests fail, check:
1. Database is properly populated
2. API is running on correct port (5001)
3. All dependencies are installed
4. File permissions are correct
5. No firewall blocking localhost connections

## Grading Alignment

This test suite directly addresses the grading criteria:

1. **CSV Converter Testing** - Tests original and arbitrary CSV files
2. **API Functionality** - Comprehensive endpoint testing
3. **SQL Injection Protection** - Security validation
4. **Data Integrity** - Database structure and content validation
5. **Performance** - Response time and efficiency testing

## Test Reports

The test runner generates:
- Console output with detailed results
- JSON report (`test_report.json`) for programmatic analysis
- HTML report (`test_report.html`) for visual review (if pytest-html available)

## Continuous Integration

For CI/CD pipelines, use:
```bash
python run_tests.py all
```

The exit code will be 0 for success, 1 for failure, making it suitable for automated testing.

## Support

If you encounter issues with the test suite:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Run individual test files to isolate issues
4. Check the console output for specific error messages

The test suite is designed to be comprehensive and should catch all issues that would cause grading failures.
