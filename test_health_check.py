"""
Test script for health check endpoints
"""
import asyncio
import httpx
import json
from datetime import datetime


async def test_health_endpoints():
    """Test both health check endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test comprehensive health check
            print("Testing /health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print("Health Check Response:")
                print(json.dumps(health_data, indent=2))
                
                # Validate response structure
                required_fields = ["status", "timestamp", "uptime_seconds", "database", "system", "services"]
                missing_fields = [field for field in required_fields if field not in health_data]
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print("✅ All required fields present")
                    
                # Check if status is healthy
                if health_data.get("status") == "healthy":
                    print("✅ System status: healthy")
                else:
                    print(f"⚠️ System status: {health_data.get('status')}")
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                print(response.text)
            
            print("\n" + "="*50 + "\n")
            
            # Test simple health check
            print("Testing /health/simple endpoint...")
            response = await client.get(f"{base_url}/health/simple")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                simple_health = response.json()
                print("Simple Health Check Response:")
                print(json.dumps(simple_health, indent=2))
                
                if simple_health.get("status") == "healthy":
                    print("✅ Simple health check: healthy")
                else:
                    print(f"⚠️ Simple health check: {simple_health.get('status')}")
            else:
                print(f"❌ Simple health check failed with status {response.status_code}")
                print(response.text)
                
        except httpx.ConnectError:
            print("❌ Could not connect to the server. Make sure the FastAPI app is running on localhost:8000")
        except Exception as e:
            print(f"❌ Error testing health endpoints: {e}")


if __name__ == "__main__":
    print("Health Check Endpoint Test")
    print("=" * 30)
    print("Make sure your FastAPI server is running on localhost:8000")
    print("You can start it with: python app.py")
    print("=" * 30)
    
    asyncio.run(test_health_endpoints())
