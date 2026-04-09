from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, models
import string, random
from fastapi.responses import RedirectResponse
from fastapi import HTTPException


models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to generate a short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/shorten_url")
def shorten_url(original_url: str, db: Session = Depends(get_db)):
    # Check if URL already exists
    existing_url = db.query(models.URL).filter(models.URL.original_url == original_url).first()
    if existing_url:
        return {"shortened_url": f"http://short.url/{existing_url.short_code}"}

    # Generate a unique short code
    short_code = generate_short_code()
    
    # Optional: ensure uniqueness in DB (loop until unique)
    while db.query(models.URL).filter(models.URL.short_code == short_code).first():
        short_code = generate_short_code()

    # Save to database
    new_url = models.URL(original_url=original_url, short_code=short_code)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {"shortened_url": f"http://short.url/{new_url.short_code}"}

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if url_entry:
        return RedirectResponse(url=url_entry.original_url)
    else:
        raise HTTPException(status_code=404, detail="URL not found")