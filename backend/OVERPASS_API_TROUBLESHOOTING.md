# Overpass API Troubleshooting Guide

## Common Errors and Solutions

### Error: "Overpass API failed" or Connection Timeout

#### Possible Causes:

1. **Internet Connection**
   - Check if you can access the internet
   - Try: `ping overpass-api.de`

2. **Query Too Large**
   - Karnataka state query might be too large
   - Solution: Use smaller area (Bangalore city instead of whole state)

3. **Overpass API Server Down**
   - The default server might be overloaded
   - Solution: Code now tries multiple servers automatically

4. **Rate Limiting**
   - Too many requests in short time
   - Solution: Wait 5-10 minutes and try again

5. **Firewall/Proxy Issues**
   - Corporate network blocking external API calls
   - Solution: Check firewall settings

## Quick Fixes

### 1. Test API Connection
```bash
cd backend
python test_overpass_api.py
```
This will test if Overpass API is reachable with simple queries.

### 2. Use Smaller Query
The code now defaults to Bangalore city instead of entire Karnataka state.
This is faster and less likely to timeout.

### 3. Increase Timeout
If you need the full Karnataka data, you can:
- Edit `QUERY` in `app/routes/transit.py`
- Change `[timeout:60]` to `[timeout:300]` (5 minutes)

### 4. Check Network
```powershell
# Test if Overpass API is reachable
Test-NetConnection overpass-api.de -Port 443
```

## Alternative: Use Sample Data

If Overpass API continues to fail, you can manually insert sample data:

```python
from app import create_app, db
from app.models import TransitNode

app = create_app()
with app.app_context():
    node = TransitNode(
        osm_id="17327417",
        type="bus_stop",
        name="Escorts Yelahanka Road",
        latitude=13.1023262,
        longitude=77.5859726
    )
    db.session.add(node)
    db.session.commit()
    print("Sample data inserted!")
```

## Still Having Issues?

1. Run `python test_overpass_api.py` and share the output
2. Check your internet connection
3. Try accessing Overpass API in browser: https://overpass-api.de/api/interpreter
4. Check if you're behind a corporate firewall/proxy

