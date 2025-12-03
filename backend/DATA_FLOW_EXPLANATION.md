# Data Loading Flow Explanation

## How Data Gets Loaded into Postgres

### Flow Diagram:
```
1. User/Client
   ↓
2. POST /transit/load_transit endpoint
   ↓
3. fetch_overpass_data() - Gets JSON from Overpass API
   ↓
4. insert_transit_nodes() - Parses JSON and inserts into DB
   ↓
5. db.session.commit() - Saves to Postgres
   ↓
6. Data appears in transit_nodes table
```

### Step-by-Step Process:

#### Step 1: API Request
- **Endpoint**: `POST http://localhost:5000/transit/load_transit`
- **What happens**: Flask receives the POST request

#### Step 2: Fetch from Overpass API
- **Function**: `fetch_overpass_data(QUERY)` in `utils/overpass_client.py`
- **What happens**: 
  - Sends POST request to Overpass API with the query
  - Query searches for bus stops, subway entrances, and stations in Karnataka
  - Returns JSON with all matching nodes

#### Step 3: Parse and Insert
- **Function**: `insert_transit_nodes(data)` in `utils/overpass_parser.py`
- **What happens**:
  - Loops through each element in the JSON
  - Filters for nodes with type="node"
  - Extracts: id, lat, lon, tags
  - Determines transit type from tags (bus_stop, railway_station, subway_entrance)
  - Checks if node already exists (by osm_id)
  - If new: Creates TransitNode and adds to session
  - If exists: Updates existing node
  - **COMMITS** to database with `db.session.commit()`

#### Step 4: Verify Data
- **Endpoint**: `GET http://localhost:5000/transit/all`
- **What happens**: Queries all TransitNode records and returns as JSON

## Common Issues:

1. **Data not appearing?**
   - Check if `db.session.commit()` is being called
   - Check if there are any errors during insertion
   - Verify database connection is correct
   - Check if data is being skipped (no valid transit_type)

2. **No data from API?**
   - Check internet connection
   - Overpass API might be slow or timeout
   - Query might not match any nodes

3. **Transaction not committed?**
   - Make sure Flask app context is active
   - Check for exceptions that prevent commit

