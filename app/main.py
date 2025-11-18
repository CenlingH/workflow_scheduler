from fastapi import FastAPI, Header
import uuid
from .models import Workflow, Job
from .scheduler import scheduler

app = FastAPI()

@app.post("/workflow")
def create_workflow(data: dict, x_user_id: str = Header(...)):
    jobs = [
        Job(
            job_id=item["job_id"],
            branch=item["branch"]
        )
        for item in data["jobs"]
    ]
    wf = Workflow(
        workflow_id=str(uuid.uuid4()),
        user_id=x_user_id,
        jobs=jobs
    )
    status = scheduler.submit_workflow(wf)
    return {"workflow_id": wf.workflow_id, "status": status}


@app.get("/workflow/{workflow_id}")
def get_workflow_status(workflow_id: str, x_user_id: str = Header(...)):
    for wf in scheduler.user_workflows[x_user_id]:
        if wf.workflow_id == workflow_id:
            return wf
    return {"error": "workflow not found"}
