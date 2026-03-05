# api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Any, Dict

from uuid import uuid4
from pathlib import Path

from generators.parsing import parse_bytes

# старые endpoints (parse-and-save) используют эти функции
from saver.save_data_to_db import save_data_to_db_api
from saver.save_data_to_file import save_data_to_file_api

# новые endpoints (uploads/ingest/raw) используют эти функции
from saver.save_data_to_db import (
    init_uploads_storage_db,
    create_upload_row,
    get_upload_row,
    insert_raw_records_rows,
    get_raw_records_rows,
)
from saver.save_data_to_file import save_upload_file_api

router = APIRouter(tags=["dataset"])


@router.on_event("startup")
def _startup():
    # создаём таблицы uploads/raw_records (SQLite или твоя реализация)
    init_uploads_storage_db()


# -------------------------
# Старые endpoints
# -------------------------

@router.post("/parse")
async def parse_endpoint(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Загружаем файл -> парсим -> возвращаем список объектов (list[dict]).
    Поддержка зависит от parse_bytes(): csv/json/jsonl/log/txt и т.д.
    """
    raw = await file.read()

    try:
        data = parse_bytes(raw, filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    preview = data[:20] if isinstance(data, list) else data

    return {
        "filename": file.filename,
        "count": len(data) if isinstance(data, list) else None,
        "preview_first_20": preview,
    }


@router.post("/parse-and-save")
async def parse_and_save_endpoint(
    file: UploadFile = File(...),

    # куда сохранять
    to_db: bool = True,
    to_file: bool = False,

    # --- параметры БД ---
    table_name: str = "events",
    dbname: str = "mldb",
    user: str = "adm",
    password: str = "P@ssw0rd",
    host: str = "192.168.0.201",
    port: str = "5432",
    create_table: bool = True,

    # --- параметры файла ---
    file_path: str = "output.csv",
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    1) Загружаем файл
    2) Парсим в list[dict]
    3) Сохраняем в БД и/или CSV

    Пример:
    - to_db=true: вставка в Postgres
    - to_file=true: сохранение в CSV
    """
    raw = await file.read()

    try:
        data = parse_bytes(raw, filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")

    if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
        raise HTTPException(status_code=400, detail="Parser must return list[dict]")

    result: Dict[str, Any] = {
        "filename": file.filename,
        "count": len(data),
        "saved": {},
    }

    # Сохранение в БД
    if to_db:
        try:
            inserted = save_data_to_db_api(
                data=data,
                table_name=table_name,
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                create_table=create_table,
            )
            result["saved"]["db"] = {"inserted_rows": inserted, "table": table_name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB save error: {e}")

    # Сохранение в файл
    if to_file:
        try:
            saved_path = save_data_to_file_api(
                data=data,
                file_path=file_path,
                overwrite=overwrite,
            )
            result["saved"]["file"] = {"path": saved_path}
        except FileExistsError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File save error: {e}")

    if not to_db and not to_file:
        result["saved"]["warning"] = "Nothing saved (to_db=false and to_file=false)"

    return result


# -------------------------
# Новые endpoints по ТЗ
# -------------------------

@router.post("/uploads")
async def uploads_create(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Шаг 1 — загрузка файла:
    - сохраняем на диск
    - создаём запись uploads в БД
    - возвращаем upload_id
    """
    upload_id = str(uuid4())
    content = await file.read()

    saved_path = save_upload_file_api(
        upload_id=upload_id,
        filename=file.filename,
        content=content,
    )

    create_upload_row(
        upload_id=upload_id,
        filename=file.filename,
        path=saved_path,
    )

    return {"upload_id": upload_id, "filename": file.filename}


@router.post("/pipeline/{upload_id}/ingest")
def pipeline_ingest(upload_id: str) -> Dict[str, Any]:
    """
    Шаг 2 — ingest:
    - читаем файл по upload_id
    - parse_bytes(raw_bytes, filename)
    - сохраняем rows в raw_records
    - возвращаем статистику
    """
    upload = get_upload_row(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="upload_id not found")

    raw_bytes = Path(upload["path"]).read_bytes()

    parse_errors = 0
    try:
        rows = parse_bytes(raw_bytes, filename=upload["filename"])
    except Exception:
        rows = []
        parse_errors = 1

    if rows and (not isinstance(rows, list) or not isinstance(rows[0], dict)):
        raise HTTPException(status_code=400, detail="Parser must return list[dict]")

    parsed_count = len(rows)
    raw_count = insert_raw_records_rows(upload_id, rows) if rows else 0

    return {
        "upload_id": upload_id,
        "raw_count": raw_count,
        "parsed_count": parsed_count,
        "parse_errors": parse_errors,
    }


@router.get("/uploads/{upload_id}/raw")
def uploads_raw(upload_id: str, limit: int = 20) -> Dict[str, Any]:
    """
    Шаг 3 — просмотр сырья:
    отдаём первые N записей raw_records для upload_id
    """
    upload = get_upload_row(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="upload_id not found")

    items = get_raw_records_rows(upload_id, limit=limit)

    return {
        "upload_id": upload_id,
        "limit": limit,
        "count": len(items),
        "items": items,
    }