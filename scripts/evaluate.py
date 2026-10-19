import asyncio,json
from app.database import Base,engine,SessionLocal
from app.seed import main as seed
from app.evaluation import evaluate
async def run():
    Base.metadata.create_all(bind=engine); seed(); db=SessionLocal()
    try: print(json.dumps(await evaluate(db),indent=2))
    finally: db.close()
if __name__=="__main__": asyncio.run(run())
