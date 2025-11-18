from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from .models import JobStatus


MAX_WORKERS = 2            # Maximum number of jobs that can run in parallel
MAX_CONCURRENT_USERS = 3   # Maximum number of concurrent users

class Scheduler:
    """Core workflow scheduler responsible for branch-aware, multi-tenant job execution.

    Responsibilities:
        - Enforces task-level concurrency via a global worker pool.
        - Enforces user-level concurrency by limiting active users.
        - Runs jobs in serial order within the same branch (FIFO).
        - Allows parallel execution across different branches.
        - Manages job lifecycle: PENDING → RUNNING → SUCCEEDED / FAILED.
        - Handles user queuing when MAX_CONCURRENT_USERS is exceeded.
    """
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.user_workflows = defaultdict(list) # user_id → [Workflow1, Workflow2, ...]
        self.active_users = set()
        self.user_queue = []
        self.branch_queues = defaultdict(list) # (user_id, branch) → FIFO list of jobs: [job1, job2, ...]

    def submit_workflow(self, workflow):
        """Submit a new workflow for execution.

        - If user limit is reached, the user is queued.
        - Otherwise, user becomes active and their jobs are inserted into branch queues.
        - Triggers scheduling to attempt immediate execution.
        """
        user = workflow.user_id
        if user not in self.active_users:
            if len(self.active_users) < MAX_CONCURRENT_USERS:
                self.active_users.add(user)
            else:
                self.user_queue.append(user)
                return "QUEUED"

        self.user_workflows[user].append(workflow)
        for job in workflow.jobs:
            self.branch_queues[(user, job.branch)].append(job)

        self.schedule()
        return "ACCEPTED"

    def get_all_jobs(self, user):
        """Return a flat list of all jobs belonging to a user across all workflows."""
        jobs = []
        for wf in self.user_workflows[user]:
            jobs.extend(wf.jobs)
        return jobs

    def schedule(self):
        """Attempt to start all eligible jobs.

        - For each branch, picks the head of the FIFO queue.
        - A job is started only if it is still in the PENDING state.
        - Uses thread pool executor for parallel execution.
        """
        for (user, branch), queue in list(self.branch_queues.items()):
            if not queue:
                continue
            job = queue[0] 
            if job.status == JobStatus.PENDING:
                job.status = JobStatus.RUNNING
                self.executor.submit(self.run_job, user, branch, job)

    def run_job(self, user, branch, job):
        """Execute a single job using the worker backend.

        - Updates job status based on success or failure.
        - Removes job from branch queue when finished.
        - Reschedules remaining work.
        - When all jobs of a user complete, releases user slot and activates the next queued user.
        """
        from .workers import run_tiled_job
        try:
            run_tiled_job(job)
            job.status = JobStatus.SUCCEEDED
        except:
            job.status = JobStatus.FAILED
        self.branch_queues[(user, branch)].pop(0)
        self.schedule()

        if all(j.status in [JobStatus.SUCCEEDED, JobStatus.FAILED]
               for j in self.get_all_jobs(user)):
            if user in self.active_users:
                self.active_users.remove(user)
            if self.user_queue:
                next_user = self.user_queue.pop(0)
                self.active_users.add(next_user)
                self.schedule()

scheduler = Scheduler()
