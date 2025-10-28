import redis

# Connect to Redis server
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Test connection
print("Connecting to Redis...")
r.ping()
print("✓ Connected successfully!")

# Simple test
print("\nTesting basic operations...")
r.set('test_key', 'Hello Redis!')
value = r.get('test_key')
print(f"✓ Set and retrieved value: {value}")

# Clean up
r.delete('test_key')
print("✓ Test completed successfully!")

