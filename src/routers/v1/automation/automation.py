from fastapi import APIRouter, Request
#from .webhook.webhook import router as webhook_router
#from .demo.demo import router as demo_router
from .awx_launcher.awx_launcher import router as launcher_router
from .solarwinds_suppress_alerts.solarwinds_suppress_alerts import router as suppress_alerts_router
from .informational_router.informational_router import router as informational_router
from internals.process_request import ProcessRequest

router = APIRouter()
# deprecated
#router.include_router(webhook_router, prefix="/webhook")
#router.include_router(demo_router, prefix="/demo")
router.include_router(launcher_router, prefix="/awx_launch")
router.include_router(suppress_alerts_router, prefix="/awx_launch")
router.include_router(informational_router, prefix="/informational")

#@router.post("/servicenow_automation_request", tags=[f"Automation - ServiceNow Automation Request - Generic Endpoint"])
#async def SNOWAutomationRequest(request: Request):
#    #data = await request.json()
#    #print(data)
#    response = await ProcessRequest().process_servicenow_request(
#        request,
#        "v1/automation/servicenow_automation_request"
#    )
#    return response


