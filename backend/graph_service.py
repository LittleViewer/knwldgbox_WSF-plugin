import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
from config import GRAPHS_DIR as DATA_DIR

class GraphData(BaseModel):
    nodes: list
    edges: list
    nextNodeId: int


def graph_payload(payload: GraphData) -> dict[str, Any]:
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


def graph_path(filename: str, *, add_extension: bool = True) -> Path:
    name = filename.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Graph filename is required")
    if "/" in name or "\\" in name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid graph filename")
    if add_extension and not name.endswith(".json"):
        name += ".json"
    if not name.endswith(".json"):
        raise HTTPException(status_code=400, detail="Graph filename must end with .json")

    path = (DATA_DIR / name).resolve()
    if path.parent != DATA_DIR:
        raise HTTPException(status_code=400, detail="Invalid graph filename")
    return path


@router.get("/api/graphs")
async def list_graphs():
    graphs = []
    # Sort by modification time descending
    for path in sorted(DATA_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        if path.is_file():
            filename = path.name
            try:
                with path.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                nodes_count = len(data.get("nodes", []))
                edges_count = len(data.get("edges", []))
            except Exception:
                nodes_count = 0
                edges_count = 0
                
            graphs.append({
                "filename": filename,
                "name": path.stem,
                "nodes_count": nodes_count,
                "edges_count": edges_count
            })
    return {"status": "success", "graphs": graphs}

@router.get("/api/graphs/{filename}")
async def load_graph(filename: str):
    filepath = graph_path(filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Graph not found")
        
    try:
        with filepath.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/graphs/{filename}")
async def save_graph(filename: str, payload: GraphData):
    filepath = graph_path(filename)
    try:
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(graph_payload(payload), f, indent=2)
        return {"status": "success", "filename": filepath.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/graphs/{filename}")
async def delete_graph(filename: str):
    filepath = graph_path(filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Graph not found")
        
    try:
        filepath.unlink()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RenameData(BaseModel):
    newName: str

@router.put("/api/graphs/{filename}/rename")
async def rename_graph(filename: str, payload: RenameData):
    old_filepath = graph_path(filename)
    if not old_filepath.exists():
        raise HTTPException(status_code=404, detail="Graph not found")
        
    new_filepath = graph_path(payload.newName)
    if new_filepath.exists():
        raise HTTPException(status_code=400, detail="A graph with this name already exists")
        
    try:
        old_filepath.rename(new_filepath)
        return {"status": "success", "filename": new_filepath.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExportAbsoluteData(BaseModel):
    path: str
    data: dict

@router.post("/api/graphs/export_absolute")
async def export_graph_absolute(payload: ExportAbsoluteData):
    out_path = Path(payload.path).expanduser().resolve()
    if not out_path.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute")
    
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(payload.data, f, indent=2)
        return {"status": "success", "path": str(out_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
