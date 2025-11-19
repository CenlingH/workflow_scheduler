import time
import random
# These job types need to be further adjusted based on real image processing algorithms. Below are just mock implementations.

def run_segment_cells_job(job): 
    '''Simulate a long-running tiled image-processing task.

    - Splits the job into a fixed number of tiles (20).
    - Processes each tile sequentially with a delay to mimic heavy computation.
    - Updates job progress (`tiles_processed`, `progress`) after each tile.
    - Intended as a placeholder for real InstanSeg large-WSI segmentation.
    '''
    job.tiles_total = 20
    for i in range(20):
        time.sleep(0.3)   # adjust by yourself
        job.tiles_processed = i + 1
        job.progress = (i + 1) / job.tiles_total * 100


def run_tissue_mask_job(job):
    '''Simulate tissue-mask generation.'''
    job.tiles_total = 30  
    for i in range(job.tiles_total):
        time.sleep(0.2) 
        job.tiles_processed = i + 1
        job.progress = (i + 1) / job.tiles_total * 100


def run_instanseg_job(job):
    """
    Mock InstanSeg job:
    - Simulates tile overlap
    - Simulates batching
    - Simulates merging phase
    - Much slower than other jobs
    """
    TOTAL_TILES = 60
    job.tiles_total = TOTAL_TILES
    TILE_BATCH_SIZE = 8  
    TILE_SLEEP = 0.15    
    processed = 0
    while processed < TOTAL_TILES:
        batch = min(TILE_BATCH_SIZE, TOTAL_TILES - processed)
        time.sleep(TILE_SLEEP)
        processed += batch
        job.tiles_processed = processed
        job.progress = round((processed / TOTAL_TILES) * 100, 2)
    time.sleep(2.0)
    job.progress = 100


def run_tiled_job(job):
    '''Choose the correct image processing job types.'''
    # Simulate random failure for demonstration
    if job.job_type == "INSTANSEG_WSI" and random.random() < 0.05:
        raise RuntimeError(f"Job {job.job_id} failed due to simulated model error.")

    if job.job_type == "TISSUE_MASK":
        return run_tissue_mask_job(job)
    elif job.job_type == "INSTANSEG_WSI":
        return run_instanseg_job(job)
    return run_segment_cells_job(job)