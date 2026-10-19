from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base,engine,get_db
from app.models import ImageAsset,ArticlePost,Suggestion,BackgroundJob,CostEntry
from app.schemas import ImageCreate,ImageOut,PostCreate,GuardRequest,ReviewCreate
from app.guard import evaluate_match
from app.service import rank_images
from app.jobs import launch_job
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    yield
app=FastAPI(title=settings.app_name,version="0.1.0",description="Image understanding, semantic matching, and mismatch guard capstone.",lifespan=lifespan)
@app.get("/",response_class=HTMLResponse,include_in_schema=False)
def home():
    return """<!doctype html><html><head><meta charset="utf-8"><title>FlyRank Image Relevance</title><style>body{font:16px system-ui;max-width:850px;margin:4rem auto;padding:0 1rem;color:#17212b}.hero{padding:2rem;border-radius:16px;background:#eef7f5}a{color:#1264a3}</style></head><body><div class="hero"><h1>AI Image Understanding &amp; Content Matching Engine</h1><p>Rank article images and reject weak or mismatched recommendations.</p><p><a href="/docs">Open API docs</a> · <a href="/health">Health check</a></p></div><h2>Quick demo</h2><p>Seed demo data with <code>python -m app.seed</code>, then use the API docs.</p></body></html>"""
@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}
@app.get("/api/images",response_model=list[ImageOut])
def list_images(db:Session=Depends(get_db),limit:int=Query(100,ge=1,le=500)):
    return db.query(ImageAsset).order_by(ImageAsset.id).limit(limit).all()
@app.post("/api/images",response_model=ImageOut,status_code=201)
def create_image(payload:ImageCreate,db:Session=Depends(get_db)):
    if db.query(ImageAsset).filter_by(path=payload.path).first(): raise HTTPException(409,"An image with this path already exists.")
    item=ImageAsset(**payload.model_dump(),flagged_for_review=payload.confidence<settings.vision_confidence_threshold)
    db.add(item); db.commit(); db.refresh(item); return item
@app.post("/api/jobs/vision",status_code=202)
async def start_vision_job(db:Session=Depends(get_db)):
    total=db.query(ImageAsset).count()
    if total==0: raise HTTPException(400,"No images registered. Seed demo data or add images first.")
    job=BackgroundJob(kind="vision_batch",status="queued",total=total); db.add(job); db.commit(); db.refresh(job); launch_job(job.id)
    return {"job_id":job.id,"status":job.status,"total":total,"message":"Background job queued."}
@app.get("/api/jobs/{job_id}")
def get_job(job_id:int,db:Session=Depends(get_db)):
    job=db.get(BackgroundJob,job_id)
    if not job: raise HTTPException(404,"Job not found.")
    return {"job_id":job.id,"kind":job.kind,"status":job.status,"progress":job.progress,"total":job.total,"attempts":job.attempts,"error":job.error,"result":job.result}
@app.post("/api/posts",status_code=201)
def create_post(payload:PostCreate,db:Session=Depends(get_db)):
    post=ArticlePost(**payload.model_dump()); db.add(post); db.commit(); db.refresh(post)
    return {"id":post.id,"title":post.title,"content":post.content,"expected_subject":post.expected_subject}
@app.get("/api/posts")
def list_posts(db:Session=Depends(get_db)):
    return [{"id":p.id,"title":p.title,"content":p.content,"expected_subject":p.expected_subject} for p in db.query(ArticlePost).order_by(ArticlePost.id).all()]
@app.get("/api/posts/{post_id}/images")
async def match_post_images(post_id:int,limit:int=Query(10,ge=1,le=50),db:Session=Depends(get_db)):
    post=db.get(ArticlePost,post_id)
    if not post: raise HTTPException(404,"Post not found.")
    return await rank_images(db,post,limit)
@app.post("/api/matches/guard")
def guard_candidate(payload:GuardRequest,db:Session=Depends(get_db)):
    post=db.get(ArticlePost,payload.post_id); image=db.get(ImageAsset,payload.image_id)
    if not post or not image: raise HTTPException(404,"Post or image not found.")
    return evaluate_match(post,image,payload.similarity)
@app.post("/api/reviews")
def review_suggestion(payload:ReviewCreate,db:Session=Depends(get_db)):
    item=db.get(Suggestion,payload.suggestion_id)
    if not item: raise HTTPException(404,"Suggestion not found.")
    item.status="approved" if payload.decision=="approve" else "rejected"
    item.explanation=(item.explanation+f" Human review: {payload.decision}. {payload.note}").strip()
    db.commit(); return {"suggestion_id":item.id,"status":item.status,"explanation":item.explanation}
@app.get("/api/suggestions")
def list_suggestions(db:Session=Depends(get_db),limit:int=Query(100,ge=1,le=500)):
    return [{"id":s.id,"post_id":s.post_id,"image_id":s.image_id,"similarity":s.similarity,"accepted":s.accepted,"status":s.status,"explanation":s.explanation} for s in db.query(Suggestion).order_by(Suggestion.id.desc()).limit(limit).all()]
@app.get("/api/costs")
def costs(db:Session=Depends(get_db)):
    rows=db.query(CostEntry).order_by(CostEntry.id.desc()).limit(500).all()
    return {"entries":[{"id":x.id,"provider":x.provider,"operation":x.operation,"model":x.model,"reference":x.reference,"estimated_cost_usd":x.estimated_cost_usd,"duration_ms":x.duration_ms,"success":x.success,"error":x.error} for x in rows],"estimated_total_usd":round(sum(x.estimated_cost_usd for x in rows),6),"entry_count":len(rows)}
@app.post("/api/evaluation/run")
async def run_evaluation(db:Session=Depends(get_db)):
    from app.evaluation import evaluate
    return await evaluate(db)
@app.get("/api/evaluation")
def evaluation_info():
    return {"script":"python scripts/evaluate.py","dataset":"data/eval_set.json","metric":"top-1 precision","warning":"Seeded demo metric is not a real-world benchmark."}
