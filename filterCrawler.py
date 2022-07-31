import requests
import json

keySelected = 'character_region'
collectionName = 'Area'
idField = 'area_id'
nameField = 'area_name'

# Data API link from mongoDB
url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/insertOne"

# This api is get from hoyowiki website
response = requests.get('https://sg-wiki-api-static.hoyolab.com/hoyowiki/wapi/get_menu_filters?menu_id=2')
data = response.json()['data']['filters']

for i in data:
    # When found the selected key that want to crawl will loop the value and insert to mongoDB one by one
    if i['key'] == keySelected:
        # Use this incrementId as foreign key linking purpose
        incrementId = 1
        for item in i['values']:
            payload = json.dumps({
                "collection": collectionName, # May change the collectionName at the variable declaration
                "database": "<DATABASE>",
                "dataSource": "<DATASOURCE_NAME>",
                "document": {
                    idField: incrementId,
                    nameField: item['value'] # Get the value
                }
            })
            headers = {
              'Content-Type': 'application/json',
              'Access-Control-Request-Headers': '*',
              'api-key': '<API_KEY>', # Insert related API_KEY
            }
    
            response = requests.request("POST", url, headers=headers, data=payload) # Run the API to insert data
            incrementId = incrementId + 1
