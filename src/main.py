import uvicorn
from fastapi import FastAPI,Request,Header
from typing import Union
from routers.api import router as api_router
from internals.log import log, app_title
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
import os


#Metadata args for API docs - Swagger
app = FastAPI(
    title=f'{ app_title }',
    description=f'The { app_title } service is used to facilitate automation including jobs runs from upstream systems, ITOA infrastructure etc.'
)

@app.get("/")
def home():
    return {"Hello": "World"}

@app.get("/helpme", include_in_schema=False)
async def custom_swagger_ui_html(req: Request,apikey: str = ''):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    apikeytouse=apikey
    if req.headers.get('apikey'):
      apikeytouse=req.headers.get('apikey')
    return get_swagger_ui_html(
        openapi_url=openapi_url+'?apikey='+str(apikeytouse),
        title="API",
    )

@app.get("/dumptest")
async def dumpapiendpoint(request:Request='',apikey: str =''):
    return {"apikeyviaurl":apikey,"headers":request.headers,"requestbody":request.body}

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    log.info(f'{{"module":"main", "action":"", "message":"STARTED - { app_title }."}}')
    #Run API
    uvicorn.run("main:app", port=8001, access_log=True)
