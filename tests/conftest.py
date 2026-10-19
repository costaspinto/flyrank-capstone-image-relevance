import os
os.environ["DATABASE_URL"]="sqlite:///./test_image_relevance.db"
os.environ["VISION_PROVIDER"]="local"
os.environ["EMBEDDING_PROVIDER"]="local"
