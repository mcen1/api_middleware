from fastapi import APIRouter
from .automation.automation import router as automation_router
#from .team_infrastructure.team_infrastructure import router as team_infrastructure_router

router = APIRouter()
router.include_router(automation_router, prefix="/automation")
#No longer needed
#router.include_router(team_infrastructure_router, prefix="/team_infrastructure")
