# Workflow Scheduler

A lightweight **multi-tenant, branch-aware workflow scheduling system** with a fully interactive **frontend dashboard**, worker simulation, and optional **rate limiting** using Redis token bucket.

This project simulates a simplified version of a real-world image-processing workflow system (such as InstanSeg WSI segmentation pipelines). It includes:

- 🚀 Workflow creation API (FastAPI)
- 🧵 Branch-aware job scheduler (FIFO per branch)
- 👥 Multi-user concurrency control
- 🎛️ UI Dashboard for job tracking
- 🧠 Worker simulation for tile-based image processing
- ⚡ Optional Rate Limiting (Redis Token Bucket)

## ✨ Core Features

#### **1. Workflow API (FastAPI)**

- `POST /workflow`
  - Accepts `jobs: [{job_id, branch, job_type}]`
  - Creates a workflow for a given `X-User-ID`
  - Returns workflow ID and initial status
- `GET /workflow/{workflow_id}`
  - Returns workflow + jobs + progress
  - Permission enforced per user

------

#### **2. Frontend Dashboard (HTML + JS)**

- Live status update every second
- Display:
  - Workflow ID
  - Global workflow status
  - Per-job status, tiles, progress bar
- “Create workflow” panel
- Beautiful GitHub-dark theme UI

Access UI at:

```
http://127.0.0.1:8000/ui
```

------

#### **3. Scheduler (Core Logic)**

Branch-aware, multi-tenant scheduler supporting:

- FIFO *within* a branch

- Parallel execution *across* branches

- Multi-user concurrency limiting (MAX_CONCURRENT_USERS)

- Job lifecycle:

  ```
  PENDING → RUNNING → SUCCEEDED / FAILED
  ```

When a user finishes all jobs, the next queued user starts.

------

#### **4. Worker Simulation**

Workers simulate real WSI tile-based workflows:

- `SEGMENT_CELLS`: ~20 tiles
- `TISSUE_MASK`: ~30 tiles
- `INSTANSEG_WSI`: ~60 tiles, batched, slower

Each worker updates:

- `tiles_processed`
- `tiles_total`
- `progress`

These values drive the live UI progress bars.

------

## ⭐ Bonus Features

#### **1. Redis Token Bucket Rate Limiting**

Rate limiting is applied to workflow creation:

- Maximum 10 requests per user
- Token bucket refills at 1 token/sec
- Redis keys used:
  - `bucket:{user}:tokens`
  - `bucket:{user}:timestamp`

Location of implementation:

```
app/rate_limit.py
app/main.py  (integration)
```

If rate limit exceeded, FastAPI returns:

```
429 Too Many Requests
```

This protects the backend when users spam requests.

------

## 📁 Project Structure

```
app/
  ├── main.py              # FastAPI entrypoint
  ├── models.py            # Job / Workflow models
  ├── scheduler.py         # Core scheduler logic
  ├── workers.py           # Worker job simulation
  ├── rate_limit.py        # Redis token bucket (Bonus)
  └── storage.py           # Internal storage helpers

frontend/
  └── index.html           # UI Dashboard

README.md                  # ← this file
```

------

## ▶️ Running the Project

### **1. Start Redis**

```
brew services start redis
```

Verify:

```
redis-cli ping
```

Should return:

```
PONG
```

------

### **2. Activate virtual environment**

```
source instanseg_env/bin/activate
```

------

### **3. Install dependencies**

```
pip install fastapi uvicorn redis pydantic
```

------

### **4. Start FastAPI server**

```
uvicorn app.main:app --reload --port 8000
```

------

### **5. Open Dashboard**

```
http://127.0.0.1:8000/ui
```

------

## 📘 Using Swagger API

FastAPI automatically provides an interactive API documentation page powered by **Swagger UI**.

You can access it at:

```
http://127.0.0.1:8000/docs
```

You will see **two main endpoints**:

- `POST /workflow`
- `GET /workflow/{workflow_id}`

Below is a detailed explanation of how to use them.

### 1. POST /workflow — Create a Workflow

This endpoint submits a new workflow for the current user.

#### Steps in Swagger:

1. Open
    **POST /workflow**
2. Click **"Try it out"**
3. Add a header:

| Name        | Value                         | Required |
| ----------- | ----------------------------- | -------- |
| `x-user-id` | `1` (or any user ID you want) | Yes      |

1. Fill in the request body:

##### Example request:

```
{
  "jobs": [
    { "job_id": "j1", "branch": "b1", "job_type": "SEGMENT_CELLS" },
    { "job_id": "j2", "branch": "b1", "job_type": "TISSUE_MASK" }
  ]
}
```

2. Click **Execute**

3. Expected response:

```
{
  "workflow_id": "9d2fdb1a-3f5a-4e99-8732-13418e015e19",
  "status": "ACCEPTED"
}
```

The important value here is:

```
workflow_id
```

You will use it in the GET request.

------

### 2. GET /workflow/{workflow_id} — Check Workflow Progress

This endpoint returns:

- Workflow metadata
- Job statuses
- Tile progress
- Overall workflow status

#### Steps in Swagger:

1. Open
    **GET /workflow/{workflow_id}**
2. Click **Try it out**
3. Set the **workflow_id** field using the ID returned from the POST request.
4. Add the same header:

```
x-user-id: 1
```

5. Click **Execute**

##### Example response:

```
{
  "workflow_id": "9d2fdb1a-3f5a-4e99-8732-13418e015e19",
  "user_id": "1",
  "status": "RUNNING",
  "jobs": [
    {
      "job_id": "j1",
      "job_type": "SEGMENT_CELLS",
      "state": "RUNNING",
      "tiles_total": 20,
      "tiles_processed": 6,
      "progress": 0.30
    },
    {
      "job_id": "j2",
      "job_type": "TISSUE_MASK",
      "state": "PENDING",
      "tiles_total": 30,
      "tiles_processed": 0,
      "progress": 0.00
    }
  ]
}
```

As workers continue running, repeated GET requests will show real-time progress updates.

------

### 3. Token Bucket Rate Limiting (Bonus Feature)

I implemented the **Redis Token Bucket**. This means Swagger calls will also be limited if you spam requests.

#### Limit rules:

- Bucket size = **10**
- Refill = **1 token per second**

#### What happens if you exceed the limit?

You will get:

```
429 Too Many Requests
```

Swagger will show:

```
{
  "detail": "Rate limit exceeded. Please slow down."
}
```

This confirms your bonus implementation is working perfectly.

------

#### Test Example: Triggering Rate Limit

In Swagger:

1. Keep clicking "Execute" on the `POST /workflow` rapidly
2. After around **10 clicks**, you will see:

```
429
```

Wait **1 second per new token**, then you can continue.

## **💬 Exported Per-Cell Segmentation Results (Mock Output)**

This project includes a **mock implementation** of the “per-cell segmentation results” export feature required by the challenge. Since no real WSI model inference is performed, the system generates **simulated polygon annotations** when an `INSTANSEG_WSI` job completes.

When such a job finishes successfully, the scheduler writes a file to:

```
results/<job_id>/results.json
```

The file contains **synthetic polygons**, like:

```
[
  { "id": 1, "polygon": [[1,1],[2,1],[2,2],[1,2]], "type": "cell" },
  { "id": 2, "polygon": [[3,3],[4,3],[4,4],[3,4]], "type": "cell" }
]
```

This output is **not produced by a real segmentation model**. It is lightweight and deterministic, purely to **simulate an export pipeline** and demonstrate:

- workflow → job → worker → export end-to-end flow
- directory creation (`results/<job_id>/`)
- JSON file writing
- worker/scheduler integration

## 🧠 Design Highlights

- Scheduler uses a `ThreadPoolExecutor`
- Branch isolation ensures tasks don’t cross-block
- User concurrency ensures fairness between users
- Redis Rate limiting protects system under load
- Frontend polls server in real time for progress updates

------

## 🚀 Scaling the System (Handling 10× More Users & Workloads)

To scale this system to support **10× more users and workflows**, several improvements can be applied:

- **Horizontal Scaling of Workers**
   Add more worker processes or deploy workers across multiple machines/containers. Since workers are stateless, they can scale almost linearly.
- **Shared State Storage**
   Move workflow/job status from in-memory Python structures to a shared database (Redis, PostgreSQL, or DynamoDB), allowing multiple API servers and workers to access consistent state.
- **API Server Load Balancing**
   Run multiple FastAPI instances behind a load balancer (NGINX / AWS ALB), enabling higher request throughput without blocking.
- **Redis Scaling**
   Upgrade Redis to a **clustered** or **replicated** setup to handle higher token-bucket traffic and workflow queries.
- **Queue-Based Scheduling**
   Replace in-process scheduler with a distributed message queue (Celery, Redis Queue, Kafka) to support high-throughput job dispatching.

With these changes, the system can reliably process large numbers of workflows concurrently while keeping scheduling fairness and job execution responsiveness.

## 📌 Future Improvements

- Actual WSI display + segmentation overlay
- Docker Compose deployment (API + Redis + worker)
- Prometheus metrics dashboard
- Real async workers (Celery / Redis Queue)