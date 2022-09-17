import requests
import json

# Variable declaration
url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/find"
headers = {
  'Content-Type': 'application/json',
  'Access-Control-Request-Headers': '*',
  'api-key': '<API_KEY>', 
}
payload = json.dumps({
    "collection": "<COLLECTION_NAME>",
    "database": "<DATABASE_NAME>",
    "dataSource": "<DATASOURCE_NAME>",
})
characterDetailList = []

# Get characters for link relationship later on
characterList = requests.request("POST", url, headers=headers, data=payload).json()['documents']

# First call to get number of total data
response = requests.post('https://sg-wiki-api.hoyolab.com/hoyowiki/wapi/get_entry_page_list', 
                         headers={"referer": "https://wiki.hoyolab.com/"},
                         params={"filters":[],"menu_id":"2","page_num":1,"page_size":30,"use_es":True})
totalData = response.json()['data']['total']

# Second call to get all data at a time
response = requests.post('https://sg-wiki-api.hoyolab.com/hoyowiki/wapi/get_entry_page_list', 
                         headers={"referer": "https://wiki.hoyolab.com/"},
                         params={"filters":[],"menu_id":"2","page_num":1,"page_size":totalData,"use_es":True})
dataList = response.json()['data']['list']

for item in dataList:
    # Get detail of each character
    characterInfo = requests.get('https://sg-wiki-api-static.hoyolab.com/hoyowiki/wapi/entry_page?entry_page_id=' + item['entry_page_id']).json()
    if "data" in characterInfo:
        characterId = 0
        # Find character id store in database
        for existData in characterList:
            if existData['name'] == characterInfo['data']['page']['name']:
                characterId = existData['character_id']
        
        # If character is store in database
        if characterId != 0:
            for data in characterInfo['data']['page']['modules']:
                # Find constellation detail
                if data['name'] == "Constellation":
                    # If not empty
                    if "data" in data['components'][0] and not data['components'][0]['data'] is None and not data['components'][0]['data'] == "":
                        tempList = json.loads(data['components'][0]['data'])['list']
                        
                        # Store into array with character id from database
                        index = 1
                        for detail in tempList:
                            characterDetailList.append({
                                'constellation_id': index,
                                'constellation_name': detail['name'],
                                'constellation_icon_url': detail['icon_url'],
                                'constellation_detail': detail['desc'],
                                'character_id': characterId
                                })
                            index = index + 1
                        
 
# Insert all data into database
url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/insertMany"
payload = json.dumps({
    "collection": "<COLLECTION_NAME>",
    "database": "<DATABASE_NAME>",
    "dataSource": "<DATASOURCE_NAME>",
    "documents": characterDetailList
})
response = requests.request("POST", url, headers=headers, data=payload)
