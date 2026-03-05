# api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Any, Dict, Optional

from generators.parsing import parse_bytes

# Эти импорты должны существовать (добавь API-функции в saver-файлы)
from saver.save_data_to_db import save_data_to_db_api
from saver.save_data_to_file import save_data_to_file_api

router = APIRouter(tags=["dataset"])


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

    # чтобы не вернуть гигантский JSON, дадим preview
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