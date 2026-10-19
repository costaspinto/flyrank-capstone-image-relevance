import asyncio
from app.database import SessionLocal
from app.models import BackgroundJob, ImageAsset, CostEntry
from app.providers import classify_image
from app.config import settings
async def process_job(job_id):
    db=SessionLocal()
    try:
        job=db.get(BackgroundJob,job_id)
        if not job:return
        job.status="running"; db.commit()
        images=db.query(ImageAsset).all(); job.total=len(images); db.commit(); failures=[]
        for i,image in enumerate(images,1):
            succeeded=False; error=None
            for attempt in range(settings.max_batch_retries+1):
                try:
                    fallback={"subject":image.subject,"category":image.category,"attributes":image.attributes,"caption":image.caption,"confidence":image.confidence}
                    meta,provider,model,cost,duration=await classify_image(image.path,fallback)
                    image.subject=meta.subject; image.category=meta.category; image.attributes=meta.attributes
                    image.caption=meta.caption; image.confidence=meta.confidence
                    image.flagged_for_review=meta.confidence<settings.vision_confidence_threshold; image.metadata_source=provider
                    db.add(CostEntry(provider=provider,operation="vision",model=model,reference=f"image:{image.id}",estimated_cost_usd=cost,duration_ms=duration,success=True))
                    succeeded=True; break
                except Exception as exc:
                    error=str(exc)
                    if attempt>=settings.max_batch_retries:
                        db.add(CostEntry(provider=settings.vision_provider,operation="vision",model="configured",reference=f"image:{image.id}",estimated_cost_usd=0,duration_ms=0,success=False,error=error[:1000]))
            if not succeeded: failures.append({"image_id":image.id,"error":error}); image.flagged_for_review=True
            job.progress=i; job.attempts+=1; db.commit()
        job.result={"processed":job.progress,"failed":failures}; job.status="completed" if not failures else "completed_with_errors"; db.commit()
    except Exception as exc:
        db.rollback(); job=db.get(BackgroundJob,job_id)
        if job: job.status="failed"; job.error=str(exc); db.commit()
    finally: db.close()
def launch_job(job_id):
    asyncio.create_task(process_job(job_id))
