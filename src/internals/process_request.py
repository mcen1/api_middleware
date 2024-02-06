from internals.log import log
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

class ProcessRequest():
    def __init__(self):
        pass

    async def process_servicenow_request(self, request: Request, endpoint):
        client_host = request.client.host
        log.info(
            f'{{'
            f'"module":"internals/process_servicenow_request",'
            f'"action":"servicenow_request",'
            f'"call_to":"{ endpoint }",'
            f'"call_from":"{ client_host }"'
            f'}}'
        ) 
        data = await self._process_inbound_request_data(request)
        #check if SNow payload contains the required keys
        required_keys = [
            'automation_request',
            'automation_type'
        ]
        #for k in payload.keys() if k not in required_keys:
        if not all(key in data.keys() for key in list(required_keys)):
            log.critical(
                f'{{'
                f'"module":"internals/process_servicenow_request",'
                f'"action":"process_servicenow_request_payload",'
                f'"message":"Could not find all required keys in the ServiceNow payload. Required keys `{ required_keys }`, are missing in ServiceNow payload: `{ data }`"'
                f'}}'
            )
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = (
                    f'Could not process the request received as the payload was invalid thus the request was aborted. '
                    f"Please contact the ITOA team for assistance."
                )
            )
        #redirect to appropriate automation endpoint
        try:
            automation_type = data.get('automation_type')
            automation_request = data.get('automation_request')
            response = RedirectResponse(url=f'/{ automation_type }/{ automation_request }/launch')
            return response
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"internals/process_servicenow_request",'
                f'"action":"redirect_request_to_automation_endpoint",'
                f'"message":"Could not redirect to appropriate automation endpoint at path: `/{ automation_type }/{ automation_request }/launch`. Exception: { exception }."'
                f'}}'
            )
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = (
                    f'Could not process the request received, please check the request thus the request was aborted.'
                    f"Please contact the ITOA team for assistance."
                )
            ) 
         
    async def _process_inbound_request_data(self, request: Request):
        self._validate_inbound_media_type(request)
        try:
            data = await self._get_request_json(request)
            log.info(
                f'{{'
                f'"module":"internals/_process_inbound_request_data",'
                f'"action":"process_inbound_request_data",'
                f'"message":"Incoming request with payload: `{ data }`",'
                f'}}'
            )
            return data
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"internals/process_request",'
                f'"action":"_process_inbound_request_data",'
                f'"message":"Could not process the request received, please check the request. Exception: { exception }."'
                f'}}'
            )
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail = (
                    f'Could not process the request received, please check the request thus the request was aborted.'
                    f"Please contact the ITOA team for assistance."
                )
            ) 
          
    # function checks media type to ensure it is of type `application/json`
    def _validate_inbound_media_type(self, request):
        content_type = request.headers.get("content-type", None)
        if content_type != "application/json":
            raise HTTPException(
                status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail = (
                    f"Unsupported media type {content_type} thus the request was aborted. "
                    f"Please contact the ITOA team for assistance."
                )
            )
        return {"content-type": content_type}

    async def _get_request_json(self, request: Request):
        data = await request.json()
        return data
