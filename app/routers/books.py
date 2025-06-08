from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from uuid import uuid4
from configurations import collection
from app.schemas import all_data
from app.models import Book
import csv
from io import StringIO
from logger import logger
from app.auth.auth_bearer import get_current_user

router = APIRouter(
    prefix="/books",
    tags=["books"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
async def get_all_books():
    logger.info("Fetching all books")
    try:
        data = list(collection.find())
        return all_data(data)
    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

@router.post("/")
async def create_book(new_book: Book):
    logger.info(f"Creating book with title: {new_book.title}")
    try:
        if collection.find_one({"title": new_book.title}):
            logger.warning(f"Book creation failed - duplicate title: {new_book.title}")
            raise HTTPException(status_code=400, detail="Book title already exists")

        book_dict = new_book.model_dump()
        book_dict["id"] = str(uuid4())
        collection.insert_one(book_dict)

        logger.info(f"Book created successfully with id: {book_dict['id']}")
        return {
            "status_code": 200,
            "message": "Book created successfully",
            "id": book_dict["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail=f"Some error occurred: {e}")

@router.get("/{book_id}")
async def get_book_by_id(book_id: str):
    logger.info(f"Fetching book with id: {book_id}")
    try:
        existing_book = collection.find_one({"id": book_id})
        if not existing_book:
            logger.warning(f"Book not found with id: {book_id}")
            raise HTTPException(status_code=404, detail="Book not exists")

        existing_book["_id"] = str(existing_book["_id"])
        logger.info(f"Book fetched successfully with id: {book_id}")
        return {
            "status_code": 200,
            "message": "Book fetched successfully",
            "data": existing_book,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book by id {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Some error occurred: {e}")

@router.put("/{book_id}")
async def update_book(book_id: str, updated_book: Book):
    logger.info(f"Updating book with id: {book_id}")
    try:
        if not collection.find_one({"id": book_id}):
            logger.warning(f"Book update failed - not found id: {book_id}")
            raise HTTPException(status_code=404, detail="Book not exists")

        if collection.find_one({"title": updated_book.title, "id": {"$ne": book_id}}):
            logger.warning(f"Book update failed - duplicate title: {updated_book.title}")
            raise HTTPException(status_code=400, detail="Book title already exists")

        collection.update_one({"id": book_id}, {"$set": updated_book.model_dump()})
        logger.info(f"Book updated successfully with id: {book_id}")
        return {
            "status_code": 200,
            "message": "Book updated successfully",
            "id": book_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating book id {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Some error occurred: {e}")

@router.delete("/{book_id}")
async def delete_book(book_id: str):
    logger.info(f"Deleting book with id: {book_id}")
    try:
        if not collection.find_one({"id": book_id}):
            logger.warning(f"Book deletion failed - not found id: {book_id}")
            raise HTTPException(status_code=404, detail="Book not exists")

        collection.delete_one({"id": book_id})
        logger.info(f"Book deleted successfully with id: {book_id}")
        return {
            "status_code": 200,
            "message": "Book deleted successfully",
            "id": book_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting book id {book_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Some error occurred: {e}")

@router.post("/import-csv/")
async def import_books_csv(file: UploadFile = File(...)):
    logger.info(f"Importing books from CSV file: {file.filename}")
    if not file.filename.endswith('.csv'):
        logger.warning("Import failed - file not CSV")
        raise HTTPException(status_code=400, detail="File must be CSV")

    try:
        contents = await file.read()
        s = contents.decode('utf-8')
        f = StringIO(s)
        reader = csv.DictReader(f)

        inserted_ids = []
        for row in reader:
            book_dict = {
                "id": str(uuid4()),
                "title": row.get("title", "").strip(),
                "author": row.get("author", "").strip(),
                "description": row.get("description", "").strip(),
                "year": int(row.get("year", 0)),
            }
            collection.insert_one(book_dict)
            inserted_ids.append(book_dict["id"])
            collection.update_one(
                {"id": book_dict["id"]},
                {"$setOnInsert": book_dict},
                upsert=True
            )
        if not inserted_ids:
            logger.warning("No books were imported from the CSV file")
            raise HTTPException(status_code=400, detail="No valid books found in the CSV file")
        
        if len(inserted_ids) != len(set(inserted_ids)):
            logger.warning("Duplicate book entries found in the CSV file")
            raise HTTPException(status_code=400, detail="Duplicate book entries found in the CSV file")
        
        if len(inserted_ids) > 1000:
            logger.warning("Too many books imported from CSV, limit is 1000")
            raise HTTPException(status_code=400, detail="Too many books imported from CSV, limit is 1000")

        logger.info(f"Imported {len(inserted_ids)} books successfully from CSV")
        return {
            "status_code": 200,
            "message": f"Imported {len(inserted_ids)} books successfully",
            "inserted_ids": inserted_ids
        }
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error importing CSV: {e}")
