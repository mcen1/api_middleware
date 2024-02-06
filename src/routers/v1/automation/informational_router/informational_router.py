from fastapi import APIRouter, Request, status, Header
from fastapi.responses import JSONResponse
from internals.process_request import ProcessRequest
from internals.apirules import *
from internals.getsnow import *
from internals.getsectigo import *
from pydantic import BaseModel
import json
class SNOWThing(BaseModel):
  item_id: str = ""

class SectigoReq(BaseModel):
  cn: str = ""
  download_type: str = "pemia"
  customer: str = "Company"


router = APIRouter()

@router.post("/snow_item_info", status_code=200, tags=[f"Informational - Get information from a Service Now item (change, request, etc)"])
def retrieveInfoFromSNOWAPI(snowthing:SNOWThing,req: Request,apikey: str = ''):
  endpoint = f"snow_item_info"
  apikeytouse=apikey
  if req.headers.get('apikey'):
    apikeytouse=req.headers.get('apikey')
  results=evaluateRulesValidityOnly(apikeytouse)
  if results!="OK":
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
    content={"errors": f"{results}"}
    )
  snowResults=getSNOWItem(snowthing.item_id)
  return JSONResponse(
  status_code=status.HTTP_200_OK,
  content={"results": snowResults}
  )

# getSectigoCert("ap-staging.domain.CompanyCompany.com")

@router.post("/get_sectigo_current_signed_cert", status_code=200, tags=[f"Informational - Get base64 encoded cert"])
def retrieveInfoFromSNOWAPI(sectigoreq:SectigoReq,req: Request,apikey: str = ''):
  endpoint = f"get_sectigo_current_signed_cert"
  apikeytouse=apikey
  if req.headers.get('apikey'):
    apikeytouse=req.headers.get('apikey')
  results=evaluateRulesValidityOnly(apikeytouse)
  if results!="OK":
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
    content={"errors": f"{results}"}
    )
  sectigoResults=getSectigoCert(sectigoreq.cn,sectigoreq.customer,sectigoreq.download_type)
  return JSONResponse(
  status_code=status.HTTP_200_OK,
  content={"results": sectigoResults}
  )

