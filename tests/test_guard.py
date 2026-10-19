from types import SimpleNamespace
from app.guard import evaluate_match
def image(subject="red fox",confidence=.9,flagged=False,category="animal"):
    return SimpleNamespace(subject=subject,confidence=confidence,flagged_for_review=flagged,category=category)
def post(expected="red fox"): return SimpleNamespace(expected_subject=expected)
def test_correct_high_confidence_match_passes(): assert evaluate_match(post(),image(),.8)["accepted"]
def test_wolf_rejected_for_fox_post():
    result=evaluate_match(post(),image("gray wolf"),.9)
    assert not result["accepted"] and any("Subject mismatch" in x for x in result["reasons"])
def test_low_confidence_rejected():
    result=evaluate_match(post(),image(confidence=.2),.8)
    assert not result["accepted"] and any("confidence" in x.lower() for x in result["reasons"])
def test_low_similarity_rejected():
    result=evaluate_match(post(),image(),.01)
    assert not result["accepted"] and any("Similarity" in x for x in result["reasons"])
