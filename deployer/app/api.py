import base64
import io
import os
import shutil
import uuid
import zipfile

from fastapi import Request, HTTPException, Depends, APIRouter
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import Config
from app.database import get_db

router = APIRouter()


@router.post("/deploy/", response_model=schemas.Website)
async def deploy(upload: schemas.WebsiteCreate, request: Request, db: Session = Depends(get_db)):
    # 1. Generate a unique ID for this new site
    site_id = str(uuid.uuid4())
    site_dir = os.path.join(Config.DEPLOYED_SITES_DIR, site_id)

    try:
        # 2. Decode the base64 string to bytes
        try:
            zip_data = base64.b64decode(upload.zip_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 string.")

        zip_file_in_memory = io.BytesIO(zip_data)

        # 3. Securely unzip the file
        with zipfile.ZipFile(zip_file_in_memory, 'r') as zip_ref:
            if not zip_ref.infolist():
                raise HTTPException(status_code=400, detail="The zip file is empty.")

            # Check for 'index.html' at the root
            if "index.html" not in [f.filename for f in zip_ref.infolist() if not f.is_dir()]:
                # Also check for nested index.html (e.g., "my-site/index.html")
                root_dirs = list(set([f.filename.split('/')[0] for f in zip_ref.infolist() if '/' in f.filename]))
                if not any(f"{d}/index.html" in [f.filename for f in zip_ref.infolist()] for d in root_dirs):
                    raise HTTPException(status_code=400,
                                        detail="Zip file must contain an 'index.html' at its root or in a single sub-directory.")

            os.makedirs(site_dir, exist_ok=True)

            # Iterate and extract files manually to prevent path traversal
            for member in zip_ref.infolist():
                # Normalize the path
                path = os.path.normpath(member.filename)

                # Skip directories and any malicious paths
                if member.is_dir() or path.startswith(('/', '../')):
                    continue

                target_file = os.path.join(site_dir, path)

                # Create subdirectories if they don't exist
                target_dir = os.path.dirname(target_file)
                os.makedirs(target_dir, exist_ok=True)

                # Write the file data
                with zip_ref.open(member) as source, open(target_file, "wb") as target:
                    shutil.copyfileobj(source, target)

        # 4. Return the new URL
        base_url = str(request.base_url)
        new_site_url = f"{base_url}sites/{site_id}/"

        return crud.create_website(db, schemas.Website(name=upload.name, url=new_site_url))

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupt zip file.")

    except Exception as e:
        # Cleanup: If anything went wrong, remove the partial directory
        if os.path.isdir(site_dir):
            shutil.rmtree(site_dir)
        print(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


# --- Endpoint 2: Static Site Server ---

# Note: These two endpoints must be in this order (most specific to least specific)

@router.get("/sites/{site_id}/")
async def get_site_index(site_id: str):
    site_dir = os.path.join(Config.DEPLOYED_SITES_DIR, site_id)
    index_file = os.path.join(site_dir, "index.html")

    # Handle common case where zip file has a single root folder
    # e.g., my-site.zip -> "my-site/index.html"
    if not os.path.isfile(index_file):
        try:
            # Get all items in the site_dir
            items = os.listdir(site_dir)

            # Filter for directories
            dirs = [item for item in items if os.path.isdir(os.path.join(site_dir, item))]

            # If there is *exactly one* directory, assume it's the root
            if len(dirs) == 1:
                nested_index = os.path.join(site_dir, dirs[0], "index.html")
                if os.path.isfile(nested_index):
                    # Redirect the user to the correct path
                    # e.g., /sites/id/ -> /sites/id/my-site-folder/
                    return RedirectResponse(url=f"./{dirs[0]}/")

        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Site not found")

        except Exception:
            pass  # Fall through to the 404 below

    if not os.path.isfile(index_file):
        raise HTTPException(status_code=404, detail="Site not found or index.html is missing.")

    return FileResponse(index_file)


<<<<<<< HEAD
@router.get("/demo-website/")
async def get_demo_website():
    site_dir = os.path.join(Config.DEPLOYED_SITES_DIR, "test")
    index_file = os.path.join(site_dir, "index.html")

    if not os.path.isfile(index_file):
        raise HTTPException(status_code=404, detail="Site not found or index.html is missing.")

    return FileResponse(index_file)


=======
>>>>>>> main-holder
@router.get("/sites/{site_id}/{file_path:path}")
async def get_site_file(site_id: str, file_path: str):
    try:
        # Get absolute paths
        abs_sites_dir = os.path.abspath(Config.DEPLOYED_SITES_DIR)
        abs_site_dir = os.path.abspath(os.path.join(Config.DEPLOYED_SITES_DIR, site_id))
        abs_file_loc = os.path.abspath(os.path.join(abs_site_dir, file_path))

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    # 1. Check if the site directory itself exists
    if not os.path.isdir(abs_site_dir):
        raise HTTPException(status_code=404, detail="Site not found")

    # 2. Check that the resolved file path is still inside its designated site directory
    if not abs_file_loc.startswith(abs_site_dir):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    # 3. Check if the file exists
    if not os.path.isfile(abs_file_loc):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(abs_file_loc)


# --- Endpoint 3: Crud Operations ---

@router.get("/read-site/{site_id}", response_model=schemas.Website)
def read_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.read_website(db, site_id)


@router.get("/read-site/", response_model=schemas.Website)
def read_all_sites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.read_all_websites(db, skip, limit)


@router.put("/update-site/{site_id}", response_model=schemas.Website)
def update_site(site_id: uuid.UUID, site_update: schemas.WebsiteUpdate, db: Session = Depends(get_db)):
    return crud.update_website(db, site_id, site_update)


@router.delete("/delete-site/{site_id}", response_model=schemas.Website)
def delete_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.delete_website(db, site_id)
