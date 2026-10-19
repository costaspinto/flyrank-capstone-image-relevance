import json
from pathlib import Path
from app.models import ArticlePost
from app.service import rank_images
async def evaluate(db):
    labels=json.loads(Path("data/eval_set.json").read_text(encoding="utf-8")); total=correct=0; rows=[]
    for label in labels:
        post=db.get(ArticlePost,label["post_id"])
        if not post: continue
        result=await rank_images(db,post,limit=50)
        first=next((x for x in result["suggestions"] if x["accepted"]),None)
        predicted=first["image_id"] if first else None; total+=1
        is_correct=predicted in label["relevant_image_ids"]
        if is_correct: correct+=1
        rows.append({"post_id":post.id,"predicted_image_id":predicted,"relevant_image_ids":label["relevant_image_ids"],"correct":is_correct})
    return {"evaluated":total,"correct_top1":correct,"top1_precision":round(correct/total,4) if total else 0.0,"rows":rows,"note":"Synthetic seeded demo only; rerun with licensed photographs and hand-labeled relevance before reporting real-world performance."}
