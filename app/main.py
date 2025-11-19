from fastapi import FastAPI, Header, HTTPException
import uuid
from .models import Workflow, Job
from .scheduler import scheduler
from .rate_limit import allow_request
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")

@app.post("/workflow")
def create_workflow(data: dict, x_user_id: str = Header(...)):
    '''Endpoint to create and submit a new workflow.'''
    
    # Rate limit check
    if not allow_request(x_user_id):
        raise HTTPException(status_code=429, detail="Too Many Requests")

    jobs = [
        Job(
            job_id=item["job_id"],
            branch=item["branch"],
            job_type=item.get("job_type", "SEGMENT_CELLS")
        )
        for item in data["jobs"]
    ]

    wf = Workflow(
        workflow_id=str(uuid.uuid4()),
        user_id=x_user_id,
        jobs=jobs
    )

    status = scheduler.submit_workflow(wf)

    return {
        "workflow_id": wf.workflow_id,
        "status": status
    }

@app.get("/workflow/{workflow_id}")
def get_workflow_status(workflow_id: str, x_user_id: str = Header(...)):
    """Get full workflow status by workflow_id."""    
    wf = scheduler.workflow_index.get(workflow_id)
    if not wf:
        return {"error": "workflow not found"}
    if wf.user_id != x_user_id:
        return {"error": "permission denied"}
    return wf