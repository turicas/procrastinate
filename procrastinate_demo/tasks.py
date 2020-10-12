import logging
import os
import random

from procrastinate import jobs
from procrastinate_demo.app import app

logger = logging.getLogger(__name__)


@app.task(queue="sums")
def sum(a, b):
    return a + b


@app.task(queue="sleep")
async def sleep(i):
    import asyncio

    await asyncio.sleep(i)


@app.task(queue="sums")
def sum_plus_one(a, b):
    return a + b + 1


@app.task(queue="retry", retry=3)
def random_fail():
    if random.random() > 0.1:
        raise Exception("random fail")


# 6th * means "every second of the minute"
@app.periodic(cron="* * * * * */10")
@app.task
async def tick(timestamp):
    logger.info(f"Tick {os.getpid()}")
    stalled_jobs = await app.job_store.get_jobs_with_status(
        status=jobs.Status.DOING, nb_seconds=60
    )
    for stalled_job in stalled_jobs:
        logger.info(f"Restart stalled job ({stalled_job.task_name}[{stalled_job.id}])")
        await app.job_store.finish_job(stalled_job, jobs.Status.TODO)
