from app.config import settings
def evaluate_match(post, image, similarity):
    reasons=[]; expected=(post.expected_subject or "").strip().lower(); subject=(image.subject or "").strip().lower()
    category=(image.category or "").strip().lower()
    if image.flagged_for_review: reasons.append("Image metadata is flagged for human review.")
    if image.confidence < settings.vision_confidence_threshold: reasons.append(f"Vision confidence {image.confidence:.2f} is below threshold {settings.vision_confidence_threshold:.2f}.")
    if expected and subject and subject not in {"unknown","unclassified"} and expected not in subject and subject not in expected:
        reasons.append(f"Subject mismatch: article expects '{expected}', image metadata says '{subject}'.")
    if expected and category == "unknown": reasons.append("Image category is unknown; subject safety cannot be confirmed.")
    if similarity < settings.match_similarity_threshold: reasons.append(f"Similarity {similarity:.3f} is below threshold {settings.match_similarity_threshold:.3f}.")
    return {"accepted":not reasons,"status":"accepted" if not reasons else "rejected","similarity":round(float(similarity),4),
        "explanation":"Match passed all guard checks." if not reasons else "Rejected: "+" ".join(reasons),"reasons":reasons}
