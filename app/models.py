from enum import Enum
from typing import List
from pydantic import BaseModel

class JobStatus(str, Enum):
    '''Enumeration of all possible states for a job in the workflow scheduler.'''
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class WorkflowStatus(Enum):
    '''Enumeration of all possible states for a workflow.'''
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class Job(BaseModel):
    """Represents a single unit of work belonging to a workflow.

    Attributes:
        job_id: Unique job identifier.
        branch: The branch this job belongs to (used for branch-aware scheduling).
        status: Current JobStatus.
        progress: Percent completion, updated during tile-based processing.
        tiles_processed: Number of processed tiles so far.
        tiles_total: Total number of tiles for this job.
    """
    job_id: str
    branch: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    tiles_processed: int = 0
    tiles_total: int = 0

class Workflow(BaseModel):
    """A workflow consists of multiple image-processing jobs for a single user.

    Attributes:
        workflow_id: Unique workflow identifier.
        user_id: Logical tenant/user identifier for multi-tenant isolation.
        jobs: Ordered list of jobs forming the workflow DAG structure.
    """
    workflow_id: str
    user_id: str
    jobs: List[Job]
    status: WorkflowStatus = WorkflowStatus.PENDING 

