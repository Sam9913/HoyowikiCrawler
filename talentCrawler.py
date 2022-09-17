import requests
import json

# Function declaration
def insertData(collection, documents):
    url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/insertMany"
    payload = json.dumps({
        "collection": collection,
        "database": "Genshin",
        "dataSource": "Cluster0",
        "documents": documents
    })
    
    requests.request("POST", url, headers=headers, data=payload)

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
characterTalentList = []
characterTalentDetail = []
characterTalentMaterial = []
levelArr = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']

# First call to get number of total data
characterList = requests.request("POST", url, headers=headers, data=payload).json()['documents']
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
                # Find talent detail
                if data['name'] == "Talents":
                    # If not empty
                    if "data" in data['components'][0] and not data['components'][0]['data'] is None and not data['components'][0]['data'] == "":
                        tempList = json.loads(data['components'][0]['data'])['list']
                        
                        # Restructure data to different table at below
                        levelId = 1
                        levelMaterialId = 1
                        index = 1
                        for detail in tempList:
                            # Store into array with character id from database
                            characterTalentList.append({
                                'talent_id': index,
                                'talent_name': detail['title'],
                                'talent_icon_url': detail['icon_url'],
                                'talent_desc': detail['desc'],
                                'character_id': characterId
                                })
                            
                            # For loop detail part
                            if not detail['attributes'] is None:
                                for attribute in detail['attributes']:
                                    if attribute['key'] != 'Level':
                                        levelIndex = 0
                                        # Store into array with talent id
                                        for levelVal in attribute['values']:
                                            characterTalentDetail.append({
                                                'talent_detail_id': levelId,
                                                'talent_detail_name': attribute['key'],
                                                'talent_level': levelArr[levelIndex],
                                                'talent_value': levelVal,
                                                'talent_id': index
                                            })
                                            
                                            if len(detail['materials']) > levelIndex and not detail['materials'][levelIndex] is None:
                                                for materialJson in detail['materials'][levelIndex]:
                                                    if not materialJson is None:
                                                        # Store into array with talent detail id
                                                        material = json.loads(materialJson.replace("$",""))[0]
                                                        characterTalentMaterial.append({
                                                            'material_id': material['ep_id'],
                                                            'material_amount': material['amount'],
                                                            'talent_detail_id': levelId,
                                                            'level_material_id': levelMaterialId
                                                        })
             
                                                        levelMaterialId = levelMaterialId + 1
                                            
                                            levelId = levelId + 1
                                            levelIndex = levelIndex + 1
                                    
                            
                            index = index + 1
     
# Insert data into multiple table    
insertData("Talent", characterTalentList)
insertData("TalentDetail", characterTalentDetail)     
insertData("TalentMaterial", characterTalentMaterial)                             
   
