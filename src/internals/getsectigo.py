import requests
import os
import json
from datetime import datetime
from pytz import timezone
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
  sectigousername = os.environ["SECTIGO_USERNAME"]
  sectigousername=sectigousername.strip()
  print(f"sectigousername found. It's {sectigousername}")
except:
  print("SECTIGO_USERNAME not defined in env!")
try:
  sectigopassword = os.environ["SECTIGO_PASSWORD"]
  sectigopassword=sectigopassword.strip()
  print(f"sectigopassword found. ")
except:
  print("SECTIGO_PASSWORD not defined in env!")

try:
  SECTIGO_BASE_URL = os.environ["SECTIGO_BASE_URL"]
  print(f"sectigo_base_url found.")
except:
  print("SECTIGO_BASE_URL not defined in env!")

def getCertFromSectigo(cert_id,customerUri="Company",download_type="pemia"):
  print(f"Gathering content for {cert_id}...")
  url=f"{SECTIGO_BASE_URL}/api/ssl/v1/collect/{cert_id}/{download_type}"
  headers={"customerUri":customerUri,"login":sectigousername,"password":sectigopassword,"Content-Type": "application/json;charset=utf-8"}
  verify=False
  try:
    x = requests.get(url, verify=False,headers=headers)
    #x = requests.get(url, verify=False,headers=headers,auth=(sectigousername,sectigopassword))
    if "description" in x.text:
      return {"errors": "unexpected result","raw":x.text}
    base64stuff=base64.b64encode(x.text.encode('utf-8'))
    return {"certificate": base64stuff.decode("utf-8")}
  except Exception as e:
    return {"errors": e,"raw":x.text}
  return {"errors":"totally failed to do anything"}


def getCNsFromSectigo(cert_dn,customerUri="Company"):
  print(f"Gathering list of DNs matching {cert_dn}...")
  print(f"Username is {sectigousername[:4]}[...]")
  url=f"{SECTIGO_BASE_URL}/api/ssl/v1?commonName={cert_dn}"
  headers={"customerUri":customerUri,"login":sectigousername,"password":sectigopassword,"Content-Type": "application/json;charset=utf-8"}
  verify=False
  try:
    x = requests.get(url, verify=False,headers=headers)
    sanitizedx=json.loads(x.text)
    json_output=sanitizedx
    ids=[]
    for item in json_output:
      ids.append(item["sslId"])
    # find highest numbered id
    if len(ids)==0:
      return {"errors": f"no matching cn's found for {cert_dn}","raw":x.text}
    return {"sslID": max(ids)} 
  except Exception as e:
    return {"errors": e,"raw":x.text}
  return {"errors":"totally failed to do anything"}


def getSectigoCert(cert_dn,customerUri="Company",download_type="pemia"):
  print(f"I was passed cert_dn={cert_dn} customerUri={customerUri} download_type={download_type}")
  myid=getCNsFromSectigo(cert_dn,customerUri)
  if "errors" in myid:
    print(myid)
    return {"errors": myid}
  content=getCertFromSectigo(myid['sslID'],customerUri,download_type)
  if "error" in content:
    return content
  return json.loads(json.dumps(content))
  

#print(getSNOWItem("INC3739931"))
#print(getSectigoCert("ap-staging.domain.CompanyCompany.com"))
