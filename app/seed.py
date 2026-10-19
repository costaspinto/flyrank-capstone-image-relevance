from pathlib import Path
from app.database import Base,engine,SessionLocal
from app.models import ImageAsset,ArticlePost
from app.config import settings
SUBJECTS={"fox":("red fox","animal",["orange fur","bushy tail","forest"],"A red fox standing among forest plants","#d97736"),"wolf":("gray wolf","animal",["gray fur","wild canine","woodland"],"A gray wolf in a woodland setting","#7b8794"),"dog":("domestic dog","animal",["pet","four legs","friendly"],"A domestic dog outdoors","#b88752"),"bear":("brown bear","animal",["brown fur","wildlife","forest"],"A brown bear in a forest","#76543c"),"deer":("red deer","animal",["antlers","meadow","wildlife"],"A red deer standing in a meadow","#b68a53")}
POSTS=[("Red foxes in woodland","A field guide to the red fox (Vulpes vulpes), orange fur, bushy tail and woodland behavior.","red fox"),("Gray wolf behavior","How gray wolves live in packs and move through woodland habitats.","gray wolf"),("Domestic dogs as companions","A guide to domestic dogs, pets, canine behavior and responsible care.","domestic dog"),("Brown bears in forests","Brown bear habitat, foraging and conservation in forest ecosystems.","brown bear"),("Red deer in the meadow","Red deer, antlers and seasonal behavior in meadow and woodland habitats.","red deer"),("Vulpes vulpes identification","Recognizing Vulpes vulpes by its orange coat, pointed ears and bushy tail.","red fox"),("Canine pack behavior","Comparing the social behavior and habitat of wild gray wolves.","gray wolf"),("Wildlife conservation basics","A broad introduction to protecting forest animals and their habitats.",None),("Marine coral reef article","Coral reefs, tropical fish, ocean biodiversity and underwater ecosystems.","coral reef"),("Space telescope discoveries","Astronomy, galaxies, distant stars and new telescope discoveries.","galaxy")]
def main():
    Base.metadata.create_all(bind=engine); assets=Path(settings.asset_dir); assets.mkdir(parents=True,exist_ok=True); db=SessionLocal()
    try:
        if db.query(ImageAsset).count()==0:
            for key,(subject,category,attrs,caption,color) in SUBJECTS.items():
                for i in range(8):
                    path=assets/f"{key}-{i+1:02d}.svg"
                    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="220" viewBox="0 0 320 220"><rect width="320" height="220" fill="#eaf3e7"/><circle cx="270" cy="35" r="18" fill="#f4d35e"/><path d="M0 175 Q80 135 150 180 T320 165 V220 H0Z" fill="#9dbb91"/><ellipse cx="160" cy="145" rx="65" ry="32" fill="{color}"/><circle cx="210" cy="105" r="31" fill="{color}"/><path d="M190 82 L183 50 L207 73 M215 74 L238 51 L235 88" fill="{color}" stroke="{color}" stroke-width="5"/><circle cx="220" cy="102" r="3" fill="#18212a"/><path d="M234 116 l10 3 -10 3" stroke="#18212a" stroke-width="2" fill="none"/><path d="M110 160 l-4 26 M148 163 l-3 23 M188 163 l2 23" stroke="#3c4638" stroke-width="8" stroke-linecap="round"/><text x="160" y="25" text-anchor="middle" font-family="Arial" font-size="12" fill="#34433a">SYNTHETIC DEMO · {subject.upper()}</text></svg>'''
                    path.write_text(svg,encoding="utf-8")
                    db.add(ImageAsset(title=f"{subject.title()} demo {i+1}",path=str(path),subject=subject,category=category,attributes=attrs,caption=caption,confidence=.88,flagged_for_review=False,metadata_source="seed-demo"))
            db.commit()
        if db.query(ArticlePost).count()==0:
            for title,content,expected in POSTS: db.add(ArticlePost(title=title,content=content,expected_subject=expected))
            db.commit()
        print(f"Seed complete: {db.query(ImageAsset).count()} images, {db.query(ArticlePost).count()} posts.")
    finally: db.close()
if __name__=="__main__": main()
