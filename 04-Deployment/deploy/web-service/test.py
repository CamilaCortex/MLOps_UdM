"""NYC Taxi Duration Prediction - Client Test Script

Test script for sending HTTP requests to the prediction service.
Useful for validating that the REST API works correctly.

Author: MLOps Team
Version: 1.0
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_prediction_api(base_url='http://localhost:9696'):
    """
    Test the API prediction endpoint.
    
    Args:
        base_url (str): Base URL of the service (default: http://localhost:9696)
    
    Returns:
        dict: API response with the prediction
    
    Example:
        >>> result = test_prediction_api()
        >>> print(f"Predicted duration: {result['duration']:.2f} minutes")
    """
    # Test data for a typical NYC trip
    ride = {
        "PULocationID": 10,   # Battery Park
        "DOLocationID": 50,   # Flatiron District
        "trip_distance": 40   # Distance in miles
    }
    
    url = f'{base_url}/predict'
    
    try:
        logger.info(f"🚕 Sending test request to {url}")
        logger.info(f"📊 Trip data: {json.dumps(ride, indent=2)}")
        
        # Send POST request
        response = requests.post(url, json=ride, timeout=10)
        
        # Check status code
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Request successful!")
            logger.info(f"📈 Predicted duration: {result.get('duration', 'N/A'):.2f} minutes")
            
            # Show complete response if it includes more fields
            if len(result) > 1:
                logger.info("📋 Complete response:")
                for key, value in result.items():
                    logger.info(f"   {key}: {value}")
            
            return result
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Error: Could not connect to server")
        logger.error("   Make sure the service is running on port 9696")
        return None
    except requests.exceptions.Timeout:
        logger.error("❌ Error: Connection timeout")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return None


def test_health_endpoint(base_url='http://localhost:9696'):
    """
    Test the health check endpoint.
    
    Args:
        base_url (str): Base URL of the service
    
    Returns:
        dict: Service status
    """
    url = f'{base_url}/health'
    
    try:
        logger.info(f"🏥 Checking health endpoint at {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info("✅ Service healthy!")
            logger.info(f"📊 Status: {health_data}")
            return health_data
        else:
            logger.error(f"❌ Health check failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in health check: {e}")
        return None


def run_comprehensive_test():
    """
    Run a comprehensive test suite for the API.
    
    Includes:
    - Health check
    - Basic prediction
    - Edge cases (long/short trips)
    """
    logger.info("🧪 Starting comprehensive test suite...")
    
    base_url = 'http://localhost:9696'
    
    # 1. Health Check
    logger.info("\n1️⃣ Testing Health Check...")
    health_result = test_health_endpoint(base_url)
    
    if not health_result:
        logger.error("❌ Health check failed, aborting tests")
        return
    
    # 2. Basic prediction
    logger.info("\n2️⃣ Testing basic prediction...")
    test_prediction_api(base_url)
    
    # 3. Edge cases
    logger.info("\n3️⃣ Testing edge cases...")
    
    # Short trip
    short_trip = {
        "PULocationID": 161,  # Times Square
        "DOLocationID": 162,  # Nearby zone
        "trip_distance": 0.5
    }
    
    # Long trip
    long_trip = {
        "PULocationID": 1,    # Newark Airport
        "DOLocationID": 263,  # JFK Airport
        "trip_distance": 25.0
    }
    
    test_cases = [
        ("Short trip", short_trip),
        ("Long trip", long_trip)
    ]
    
    for case_name, trip_data in test_cases:
        logger.info(f"\n   🔍 Case: {case_name}")
        try:
            url = f'{base_url}/predict'
            response = requests.post(url, json=trip_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                duration = result.get('duration', 0)
                logger.info(f"   ✅ {case_name}: {duration:.2f} minutes")
            else:
                logger.error(f"   ❌ {case_name} failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Error in {case_name}: {e}")
    
    logger.info("\n🎉 Test suite completed!")


if __name__ == "__main__":
    """
    Run tests when the script is executed directly.
    """
    logger.info("🚀 Starting test client for NYC Taxi API...")
    
    # Run comprehensive test suite
    run_comprehensive_test()