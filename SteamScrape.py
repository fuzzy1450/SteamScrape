import sys, math, datetime
import string, re
import json, csv
import aiohttp, asyncio



global CSV_Writer, f

DataFilePath = "./data.csv"
f = open(DataFilePath, "w")
CSV_Writer = csv.writer(f)
CSV_Writer.writerow(['name', 'appid', 'positive_reviews', 'negative_reviews', 'owner_range', 'daily_peak_ccu', 'genre_one', 'genre_two', 'genre_three'])
	
	
	





async def getPage(pageNum):
	text =""
	while(1):
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(f'http://steamspy.com/api.php?request=all&page={pageNum}') as response:
					
					text = await response.text()
					if(response.status==500): #if the page doesnt exist, it will return a 500
						return
					dataJSON = json.loads(text)
					return dataJSON
			except Exception as e:
				print(f'Page {pageNum} DL Error: ', text, e)
			
async def getApp(appID):
	text =""
	while(1):
		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(f'http://steamspy.com/api.php?request=appdetails&appid={appID}') as response:

				
					text = await response.text()
					
					appData = json.loads(text)
					return appData
			except Exception as e:
				print(f'App DL Error ({appID}): ', text, e)


async def collectData(DataLimit = 10000):
	global f
	CollectionSize = 0
	percentCompleted = 0
	
	PageNums = range(math.ceil(DataLimit/1000))
	PageRequestArray = []
	for i in PageNums:
		PageRequestArray.append(asyncio.create_task(getPage(i)))
		
		
	AppRequestArray = []
	for PageRequest in PageRequestArray:
		dataJSON = await PageRequest
			
		for x in dataJSON:
			appData = await getApp(x)
			
			appNameSteralized  = re.sub(r'[^\x00-\x7f]',r'', appData["name"]).replace(",","")
			ownerRangeSteralized = appData["owners"].replace(",","")
			
			appArray = [appNameSteralized, appData["appid"], appData["positive"], appData["negative"], ownerRangeSteralized, appData["ccu"]]
			genres = appData["genre"].split(", ")
			appArray += genres


			CSV_Writer.writerow(appArray)
			CollectionSize = CollectionSize+1

			percentCompleted = (1 - (DataLimit-CollectionSize)/DataLimit) * 100
			now = datetime.datetime.now().strftime("%H:%M:%S")
			print(f'{percentCompleted:.3f}% \t [{now}]')
							
							
	
	
	f.close()
	


asyncio.run(collectData(250000))
