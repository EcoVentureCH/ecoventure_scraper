from woocommerce import API
import json

wcapi = API(
    url="https://www.ecoventure.ch", 
    consumer_key="", 
    consumer_secret="", 
    wp_api=True,  
    version="wc/v3" 
)

data = {
    "name": "Test REST API",
    "type": "crowdfunding",
    "published": 1
}

result = wcapi.post("products", data)
result = result.json()
print(result['id'])
