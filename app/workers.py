import time
# These job types need to be further adjusted based on real image processing algorithms.

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


def run_tiled_job(job):
    '''Choose the correct image processing job types.'''
    if job.job_type == "TISSUE_MASK":
        return run_tissue_mask_job(job)
    return run_segment_cells_job(job)