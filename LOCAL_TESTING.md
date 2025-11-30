# Local Testing Guide

## Step 1: Start the Flask Server

Open a terminal and run:

```bash
# Navigate to your project directory
cd /Users/michelleweon/Desktop/f25/cs1060/michelleweon-hw4

# Activate virtual environment
source venv/bin/activate

# Start the Flask server
python api/index.py
```

You should see output like:
```
 * Serving Flask app 'index'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5002
```

The server is now running on **http://localhost:5002**

## Step 2: Test the Endpoints

### Test 1: Root Endpoint (Web Interface)
Open your browser and go to:
```
http://localhost:5002/
```

You should see your web interface.

### Test 2: POST to /county_data (Main Assignment Endpoint)

Open a **new terminal** (keep the server running) and run:

```bash
# Test with valid data
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}'
```

**Expected:** JSON array with health ranking data

### Test 3: Test Error Cases

```bash
# Test 1: Teapot error (should return 418)
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"}'

# Test 2: Missing zip (should return 400)
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"measure_name":"Adult obesity"}'

# Test 3: Missing measure_name (should return 400)
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138"}'

# Test 4: Invalid ZIP (should return 404)
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"99999","measure_name":"Adult obesity"}'

# Test 5: Invalid measure_name (should return 400)
curl -X POST http://localhost:5002/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Invalid Measure"}'
```

### Test 4: Test Other Endpoints (Optional)

```bash
# Test GET endpoint
curl http://localhost:5002/api/county_data?limit=5

# Test stats endpoint
curl http://localhost:5002/api/stats

# Test ZIP info endpoint
curl http://localhost:5002/api/zip/02138
```

## Step 3: Test the Web Interface

1. Open browser to `http://localhost:5002/`
2. Try the ZIP code lookup with `02138`
3. Try the location search
4. Check that no errors appear (no "no such column" errors)

## Quick Test Script

Save this as `test_local.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:5002"

echo "Testing /county_data POST endpoint..."
echo ""

echo "1. Valid request:"
curl -X POST $BASE_URL/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}' | head -20
echo ""
echo ""

echo "2. Teapot test (should return 418):"
curl -X POST $BASE_URL/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity","coffee":"teapot"}' -w "\nHTTP Status: %{http_code}\n"
echo ""
echo ""

echo "3. Missing zip (should return 400):"
curl -X POST $BASE_URL/county_data \
  -H "Content-Type: application/json" \
  -d '{"measure_name":"Adult obesity"}' -w "\nHTTP Status: %{http_code}\n"
echo ""
echo ""

echo "4. Invalid ZIP (should return 404):"
curl -X POST $BASE_URL/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"99999","measure_name":"Adult obesity"}' -w "\nHTTP Status: %{http_code}\n"
echo ""
```

Make it executable and run:
```bash
chmod +x test_local.sh
./test_local.sh
```

## Troubleshooting

### Port Already in Use
If port 5002 is already in use:
```bash
# Kill the process using port 5002
lsof -ti:5002 | xargs kill -9

# Or use a different port
PORT=5003 python api/index.py
```

### Database Not Found
Make sure `data.db` exists in the project root:
```bash
ls -lh data.db
```

If it doesn't exist, regenerate it:
```bash
rm -f data.db
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

### Module Not Found
Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Column Errors
If you see "no such column: col_zip" errors:
- Make sure you regenerated the database with the fixed script
- Check that the database has `zip` column: `sqlite3 data.db ".schema zip_county"`
