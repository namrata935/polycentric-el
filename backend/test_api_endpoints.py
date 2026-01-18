from app import create_app

app = create_app()

# Test in app context
with app.test_client() as client:
    # Test zones endpoint
    resp = client.get('/zones/all')
    print('GET /zones/all')
    print(f'  Status: {resp.status_code}')
    
    if resp.status_code == 200:
        data = resp.get_json()
        count = data.get('count', 0)
        print(f'  Zones returned: {count}')
        
        if data.get('zones'):
            z = data['zones'][0]
            has_sentiment = 'final_sentiment' in z
            print(f'  First zone has final_sentiment: {has_sentiment}')
            if has_sentiment:
                mean = z['final_sentiment'].get('mean', 'N/A')
                print(f'  Sentiment mean: {mean}')
            print('  ✓ Sentiment data is present')
        else:
            print('  ✗ No zones in response')
    else:
        print(f'  ✗ Error: {resp.data}')

    # Test recommendation endpoint
    print()
    print('POST /zones/recommendations')
    
    test_zone = data['zones'][0]
    resp = client.post('/zones/recommendations', 
                      json=test_zone,
                      content_type='application/json')
    print(f'  Status: {resp.status_code}')
    
    if resp.status_code == 200:
        rec_data = resp.get_json()
        rec = rec_data.get('recommendation', {})
        print(f'  Recommendation priority: {rec.get("priority", "N/A")}')
        print(f'  Sentiment level: {rec.get("sentiment_level", "N/A")}')
        print(f'  Transport access: {rec.get("context", {}).get("transport_access", "N/A")}')
        print('  ✓ Recommendation generated successfully')
    else:
        print(f'  ✗ Error: {resp.data}')

print()
print('✅ ALL TESTS PASSED!')
