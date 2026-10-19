from app.embeddings import local_similarity
def test_identical_content_scores_high(): assert local_similarity("red fox in forest","red fox in forest")>.9
def test_unrelated_content_scores_low(): assert local_similarity("red fox woodland","galaxy telescope astronomy")<.2
def test_synonym_demo(): assert local_similarity("Vulpes vulpes orange coat","red fox in woodland")>=.7
