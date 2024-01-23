from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

app = FastAPI()

# Model Pydantic untuk Catatan (Note)
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str
    content: str

class NoteInDB(NoteCreate):
    id: str
    created_at: datetime
    updated_at: datetime

# Konfigurasi MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "notes_db"
COLLECTION_NAME = "notes"

# Koneksi ke MongoDB menggunakan motor_asyncio
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Fungsi utilitas untuk mengubah dokumen MongoDB menjadi model Pydantic
def mongo_to_pydantic(note):
    return NoteInDB(**note)

# Endpoint untuk membuat catatan baru
@app.post("/notes", response_model=NoteInDB)
async def create_note(note: NoteCreate):
    note_dict = note.dict()
    note_dict.update({
        "id": str(ObjectId()),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    await collection.insert_one(note_dict)
    return mongo_to_pydantic(note_dict)

# Endpoint untuk mendapatkan semua catatan
@app.get("/notes", response_model=list[NoteInDB])
async def get_notes():
    notes = await collection.find().to_list(1000)
    return [mongo_to_pydantic(note) for note in notes]

# Endpoint untuk mendapatkan satu catatan berdasarkan ID
@app.get("/notes/{note_id}", response_model=NoteInDB)
async def get_note(note_id: str):
    note = await collection.find_one({"id": note_id})
    if note:
        return mongo_to_pydantic(note)
    else:
        raise HTTPException(status_code=404, detail="Note not found")

# Endpoint untuk memperbarui catatan berdasarkan ID
@app.put("/notes/{note_id}", response_model=NoteInDB)
async def update_note(note_id: str, updated_note: NoteUpdate):
    updated_note_dict = updated_note.dict()
    updated_note_dict["updated_at"] = datetime.utcnow()

    result = await collection.update_one(
        {"id": note_id},
        {"$set": updated_note_dict}
    )

    if result.modified_count == 1:
        updated_note_dict["id"] = note_id
        return mongo_to_pydantic(updated_note_dict)
    else:
        raise HTTPException(status_code=404, detail="Note not found")

# Endpoint untuk menghapus catatan berdasarkan ID
@app.delete("/notes/{note_id}", response_model=NoteInDB)
async def delete_note(note_id: str):
    note = await collection.find_one_and_delete({"id": note_id})
    if note:
        return mongo_to_pydantic(note)
    else:
        raise HTTPException(status_code=404, detail="Note not found")
