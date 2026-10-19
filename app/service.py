from app.models import ImageAsset, Suggestion, CostEntry
from app.embeddings import similarity
from app.guard import evaluate_match
from app.config import settings
def image_text(image):
    return " ".join([image.subject,image.category,image.caption,*(image.attributes or [])])
async def rank_images(db,post,limit=10):
    ranked=[]
    for image in db.query(ImageAsset).all():
        try:
            score,provider=await similarity(image_text(image),f"{post.title}. {post.content}")
            db.add(CostEntry(provider=provider,operation="embedding_similarity",model=provider,reference=f"post:{post.id}|image:{image.id}",
                estimated_cost_usd=settings.estimated_embedding_call_cost_usd if provider!="local-lexical" else 0,duration_ms=0,success=True))
        except Exception as exc:
            score,provider=0.0,"error"
            db.add(CostEntry(provider=provider,operation="embedding_similarity",model=provider,reference=f"post:{post.id}|image:{image.id}",estimated_cost_usd=0,duration_ms=0,success=False,error=str(exc)[:1000]))
        decision=evaluate_match(post,image,score)
        ranked.append({"image_id":image.id,"title":image.title,"subject":image.subject,"category":image.category,**decision})
    ranked.sort(key=lambda x:(x["accepted"],x["similarity"]),reverse=True)
    for item in ranked[:limit]:
        db.add(Suggestion(post_id=post.id,image_id=item["image_id"],similarity=item["similarity"],accepted=item["accepted"],status=item["status"],explanation=item["explanation"]))
    db.commit(); accepted=[x for x in ranked if x["accepted"]][:limit]
    return {"post_id":post.id,"status":"suggestions" if accepted else "no_confident_match","suggestions":ranked[:limit],
            "accepted_count":len(accepted),"message":"Ranked candidates passed the mismatch guard." if accepted else "No confident match. Review rejection reasons before selecting an image."}
