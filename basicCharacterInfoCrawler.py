import requests
import json

# Variable declaration
url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/find"
headers = {
  'Content-Type': 'application/json',
  'Access-Control-Request-Headers': '*',
  'api-key': '<API_KEY>', 
}
character = []
index = 0

# Function to retrieve multiple data at a time
def get_filter_data(collectionName):
    payload = json.dumps({
        "collection": collectionName, # May change the collectionName at the variable declaration
        "database": "<DATABASE_NAME>",
        "dataSource": "<DATASOURCE_NAME>",
    })
    
    return requests.request("POST", url, headers=headers, data=payload).json()['documents']

# Retrieve all exists data for later use
areaList = get_filter_data("Area")
weaponTypeList = get_filter_data("WeaponType")
elementTypeList = get_filter_data("ElementType")

# First call to get number of total data
response = requests.post('https://sg-wiki-api.hoyolab.com/hoyowiki/wapi/get_entry_page_list', params={"filters":[],"menu_id":"2","page_num":1,"page_size":30,"use_es":True})
totalData = response.json()['data']['total']

# Second call to get all data at a time
response = requests.post('https://sg-wiki-api.hoyolab.com/hoyowiki/wapi/get_entry_page_list', params={"filters":[],"menu_id":"2","page_num":1,"page_size":totalData,"use_es":True})
dataList = response.json()['data']['list']

# For loop all data to define in your own way
for item in dataList:
    cardImgUrl = ""
    birthdayDate = ""
    houseName = ""
    area = 0
    elementType = 0
    weaponType = 0
    star = 0
    
    # Get information of character with specific id
    characterInfo = requests.get('https://sg-wiki-api-static.hoyolab.com/hoyowiki/wapi/entry_page?entry_page_id=' + item['entry_page_id']).json()
    
    # Define card image, birthday and affiliation
    if "data" in characterInfo:
        description = characterInfo['data']['page']['desc']
        headerImgUrl = characterInfo['data']['page']['header_img_url']
        for data in characterInfo['data']['page']['modules']:
            if data['name'] == "Gallery":
                cardImgUrl = json.loads(data['components'][0]['data'])['pic']
                
            if data['name'] == "Attributes":
                dataJson = json.loads(data['components'][0]['data'])
                for dataItem in dataJson['list']:
                    if dataItem['key'] == "Birthday" and not dataItem['value'] is None:
                        birthdayDate = dataItem['value'][0]
                        
                    if dataItem['key'] == "Affiliation" and not dataItem['value'] is None:
                        houseName = dataItem['value'][0]
    
    # Define area to link with the data from database
    if "character_region" in item['filter_values']:
        for areaItem in areaList:
            if areaItem['area_name'] == item['filter_values']['character_region']['values'][0]:
                area = areaItem['area_id']
                break;
    
    # Define element type to link with the data from database
    if "character_vision" in item['filter_values']:
        for elementTypeItem in elementTypeList:
            if elementTypeItem['element_type_name'] == item['filter_values']['character_vision']['values'][0]:
                elementType = elementTypeItem['element_type_id']
                break;
    
    # Define star value
    if "character_rarity" in item['filter_values']:
       star = item['filter_values']['character_rarity']['values'][0][0:1]
    
    # Define weapon type to link with the data from database   
    if "character_weapon" in item['filter_values']:
        for weaponTypeItem in weaponTypeList:
            if weaponTypeItem['weapon_type_name'] == item['filter_values']['character_weapon']['values'][0]:
                weaponType = weaponTypeItem['weapon_type_id']
                break;
            
    tempCharacter = {
        "character_id": (index + 1),
        "name": item['name'],
        "area_id": area,
        "element_type_id": elementType,
        "star": star,
        "weapon_type_id": weaponType,
        "description": description,
        "banner_image_url": headerImgUrl,
        "card_image_url": cardImgUrl,
        "birthday_date": birthdayDate,
        "house_name": houseName
    }
    
    # Insert data into array
    character.insert(index, tempCharacter)
    index = index + 1

# Insert multiple data in a time
url = "https://data.mongodb-api.com/app/data-nkmgm/endpoint/data/v1/action/insertMany"
payload = json.dumps({
    "collection": "<COLLECTION_NAME>",
    "database": "<DATABASE_NAME>",
    "dataSource": "<DATASOURCE_NAME>",
    "documents": character
})
response = requests.request("POST", url, headers=headers, data=payload)

