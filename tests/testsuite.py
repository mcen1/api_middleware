#!/bin/env python3
import traceback
import requests
import json
import sys

testsfailed=0

APP_PORT="8000"
APP_HOST="localhost"

def tallyResults(testgo,inverse=False):
#  print(f"{testgo}\n")
  if not inverse:
    if testgo['results']!="success":
      print("Failed!")
      return 1
    return 0
  else:
    if testgo['results']!="success":
      return 0
    print("Failed!")
    return 1
  return 0

def testURL(urlpath,payload,methodtype="post"):
  try:
    if methodtype=="post":
      x = requests.post(urlpath,json=payload)
    elif methodtype=="get":
      x = requests.get(urlpath,json=payload)
    y=x.text
  except Exception as e:
    return {"results":"failed","log": traceback.format_exc()}
  return y

def testLaunchAWXJob(urlpath,apikey,payload):
  try:
    rawresult=testURL(f"{urlpath}?apikey={apikey}",payload)
    testresult=json.loads(rawresult)
    if "results" in testresult and "int" in str(type(testresult["results"])):
      testresult={"results":"success"}
  except Exception as e:
    return {"results":"failed","log": traceback.format_exc(),"raw_response":rawresult}
  return testresult   

def testGetSNOW(urlpath,apikey,payload):
  try:
    rawresult=testURL(f"{urlpath}?apikey={apikey}",payload)
    testresult=json.loads(rawresult)
    if "response" in testresult['results'] and testresult['results']["response"]!="error":
      testresult={"results":"success"}
  except Exception as e:
    return {"results":"failed","log": traceback.format_exc(),"raw_response":rawresult}
  return testresult

def testGetSectigo(urlpath,apikey,payload):
  try:
    rawresult=testURL(f"{urlpath}?apikey={apikey}",payload)
    testresult=json.loads(rawresult)
    if "certificate" in testresult['results']:
      testresult={"results":"success"}
  except Exception as e:
    return {"results":"failed","log": traceback.format_exc(),"raw_response":rawresult}
  return testresult


print(f"Testing if app is running locally on {APP_HOST}:{APP_PORT}")
testresult=testURL(f"http://{APP_HOST}:{APP_PORT}",{},methodtype="get")
if "Hello" in testresult:
  print("{'results':'success'}\n")
else:
  testsfailed=testsfailed+1
  print(f"Could not find app running on {APP_HOST}:{APP_PORT}. Quitting all tests!")
  sys.exit(255)

print("Testing launching an AWX job with SME API Key...")
testresult=testLaunchAWXJob(f"http://{APP_HOST}:{APP_PORT}/api/v1/automation/awx_launch/launch_nowait",'smeAPIKey',{"job_name":"sme-jobtest"})
print(testresult)
testsfailed=testsfailed+tallyResults(testresult)

print("Testing launching an AWX job with ITOA API Key...")
testresult=testLaunchAWXJob(f"http://{APP_HOST}:{APP_PORT}/api/v1/automation/awx_launch/launch_nowait",'teamAPIKey',{"job_name":"sme-jobtest"})
print(testresult)
testsfailed=testsfailed+tallyResults(testresult)

print("Testing launching an AWX job outside of SME org with SME API Key (should not be allowed)...")
testresult=testLaunchAWXJob(f"http://{APP_HOST}:{APP_PORT}/api/v1/automation/awx_launch/launch_nowait",'smeAPIKey',{"job_name":"automation-awx-jobtesting-job"})
if 'errors' in testresult and "Cannot run a job that isn't in the AWX org the API key is tied to" in testresult['errors']:
  print("{'results':'success'}\n")
else:
  testsfailed=testsfailed+1
  

print("Testing SNOW retrieval...")
testresult=testGetSNOW(f"http://{APP_HOST}:{APP_PORT}/api/v1/automation/informational/snow_item_info",'teamAPIKey',{"item_id":"CHG0326896"})
print(f"{testresult}\n")
testsfailed=testsfailed+tallyResults(testresult)

print("Testing Sectigo retrieval...")
testresult=testGetSectigo(f"http://{APP_HOST}:{APP_PORT}/api/v1/automation/informational/get_sectigo_current_signed_cert",'teamAPIKey',{"cn":"ap-staging.domain.CompanyCompany.com"})
print(f"{testresult}\n")
testsfailed=testsfailed+tallyResults(testresult)



print(f"Number of tests failed: {testsfailed}")
sys.exit(testsfailed)
