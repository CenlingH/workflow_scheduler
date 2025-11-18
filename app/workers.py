import time

def run_tiled_job(job):
    """Simulate a long-running tiled image-processing task.

    - Splits the job into a fixed number of tiles (20).
    - Processes each tile sequentially with a delay to mimic heavy computation.
    - Updates job progress (`tiles_processed`, `progress`) after each tile.
    - Intended as a placeholder for real InstanSeg large-WSI segmentation.
    """
    job.tiles_total = 20
    for i in range(20):
        time.sleep(0.3)  
        job.tiles_processed = i + 1
        job.progress = (i + 1) / job.tiles_total * 100
