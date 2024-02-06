import requests
import os
import json
from datetime import datetime
from pytz import timezone

snusername = os.environ["SNOW_USERNAME"]
snpassword = os.environ["SNOW_PASSWORD"]
SNOW_BASE_URL = os.environ["SNOW_HOST"]

def time_in_range(start, end, x):
  if start <= end:
    return start <= x <= end
  else:
    return start <= x or x <= end

def getAllSnowCINames(mylist):
  print(f"Gathering list of CIs associated with a CR...")
  allcis=[]
  for item in mylist:
    url=f"{item['link']}"
    headers={}
    verify=False
    x = requests.get(url, verify=False,auth=(snusername, snpassword))
    sanitizedx=json.loads(x.text)
    json_output=sanitizedx["result"]
    allcis.append({"name":json_output['name'],"sys_id":json_output['sys_id']})
  return allcis

def getCRMeta(snowinfo):
  # I believe SNOW operates with changes being in the US East Timezone
  print(f"Gathering SNOW CR metadata...")
  tz = timezone('EST')
  currentDateAndTime = datetime.now(tz)
  currentTime = currentDateAndTime.strftime("%Y-%m-%d %H:%M:%S")
  ci_list=[]
  if "dict" in str(type(snowinfo['cmdb_ci'])):
    ci_list.append(snowinfo['cmdb_ci'])
  if "list" in str(type(snowinfo['cmdb_ci'])):
    ci_list=snowinfo['cmdb_ci']
  x=time_in_range(snowinfo['start_date'],snowinfo['end_date'],currentTime)
  y=getAllSnowCINames(ci_list)
  return {"inside_window_now": x, "ci_associated_to_change": y}

def getSNOWItem(item_id):
  print(f"Looking for {item_id} in SNOW on {SNOW_BASE_URL}...")
  item_id=item_id.upper()
  item_type="none"
  if item_id.startswith("INC"):
    URL_POINT=f"/api/now/table/incident?sysparm_query=number={item_id}"
    item_type="inc"
  elif item_id.startswith("CHG"):
    URL_POINT=f"/api/now/table/change_request?sysparm_query=number={item_id}"
    item_type="chg"
  elif item_id.startswith("REQ"):
    URL_POINT=f"/api/now/table/request?sysparm_query=number={item_id}"
    item_type="req"
  else:
    return {"response": "Invalid or unsupported type of ServiceNow item passed.", "status_code": 256}
  url=f"{SNOW_BASE_URL}{URL_POINT}"
  headers={}
  verify=False
  x = requests.get(url, verify=False,auth=(snusername, snpassword))
  try:
    sanitizedx=json.loads(x.text)
    json_output=sanitizedx["result"][0]
  except Exception as e:
    print(f"Exception from SNOW: {e} text is {x.text}")
    return {"response":"error","exception":str(e),"raw_response": x.text}
  metadata={}
  if item_type=="chg":
    metadata=getCRMeta(json_output)
  return {"response": json_output, "status_code": x.status_code, "team_metadata": metadata}

#print(getSNOWItem("INC3739931"))
 
