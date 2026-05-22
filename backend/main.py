import base64
import io
import json
import os
import queue
import threading
import time

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel
from sklearn.metrics import roc_auc_score

from core.extractor import FeatureExtractor
from core.patchcore import PatchCore

MEMORY_BANK_PATH = "storage/memory_bank.pkl"
os.makedirs("storage", exist_ok=True)

app = FastAPI(title="AOI Defect Detection", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

extractor = FeatureExtractor()
model = PatchCore(extractor)

if os.path.exists(MEMORY_BANK_PATH):
    model.load(MEMORY_BANK_PATH)


# ------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------

class DirRequest(BaseModel):
    image_dir: str


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.get("/")
def root():
    return RedirectResponse(url="/ui/index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "memory_bank_ready": model.memory_bank is not None,
        "threshold": model.threshold,
    }


@app.get("/build-stream")
def build_stream(image_dir: str):
    """Stream build progress via SSE. EventSource only supports GET."""
    if not os.path.isdir(image_dir):
        raise HTTPException(status_code=400, detail=f"Directory not found: {image_dir}")

    q: queue.Queue = queue.Queue()

    def do_build():
        def cb(done, total):
            q.put({"type": "progress", "done": done, "total": total})

        try:
            count = model.build(image_dir, callback=cb)
            model.save(MEMORY_BANK_PATH)
            q.put({"type": "done", "images_processed": count})
        except Exception as e:
            q.put({"type": "error", "message": str(e)})

    threading.Thread(target=do_build, daemon=True).start()

    def generate():
        while True:
            item = q.get()
            yield f"data: {json.dumps(item)}\n\n"
            if item["type"] in ("done", "error"):
                break

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/calibrate-stream")
def calibrate_stream(image_dir: str):
    """Stream calibration progress + scores via SSE."""
    if not os.path.isdir(image_dir):
        raise HTTPException(status_code=400, detail=f"Directory not found: {image_dir}")
    if model.memory_bank is None:
        raise HTTPException(status_code=400, detail="Build memory bank first.")

    q: queue.Queue = queue.Queue()

    def do_calibrate():
        def cb(done, total, score):
            q.put({"type": "progress", "done": done, "total": total, "score": round(score, 4)})

        try:
            threshold, _ = model.calibrate(image_dir, callback=cb)
            model.save(MEMORY_BANK_PATH)
            q.put({"type": "done", "threshold": round(threshold, 4)})
        except Exception as e:
            q.put({"type": "error", "message": str(e)})

    threading.Thread(target=do_calibrate, daemon=True).start()

    def generate():
        while True:
            item = q.get()
            yield f"data: {json.dumps(item)}\n\n"
            if item["type"] in ("done", "error"):
                break

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model.memory_bank is None:
        raise HTTPException(status_code=400, detail="Memory bank not ready. Run build first.")
    if model.threshold is None:
        raise HTTPException(status_code=400, detail="Threshold not set. Run calibrate first.")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    t0 = time.perf_counter()
    result = model.predict(image)
    inference_ms = round((time.perf_counter() - t0) * 1000, 1)

    _, buffer = cv2.imencode(".jpg", result["heatmap_bgr"])
    heatmap_b64 = base64.b64encode(buffer).decode("utf-8")

    return JSONResponse({
        "is_defect": result["is_defect"],
        "score": result["score"],
        "threshold": result["threshold"],
        "inference_ms": inference_ms,
        "heatmap_base64": heatmap_b64,
    })


@app.get("/benchmark-stream")
def benchmark_stream(data_dir: str = "data/transistor"):
    """Stream benchmark progress via SSE, return AUROC at the end."""
    test_dir = os.path.join(data_dir, "test")
    if not os.path.isdir(test_dir):
        raise HTTPException(status_code=400, detail=f"Test directory not found: {test_dir}")
    if model.memory_bank is None:
        raise HTTPException(status_code=400, detail="Build memory bank first.")
    if model.threshold is None:
        raise HTTPException(status_code=400, detail="Calibrate threshold first.")

    q: queue.Queue = queue.Queue()

    def do_benchmark():
        try:
            all_scores, all_labels = [], []
            category_results = []

            # Normal images
            good_dir = os.path.join(test_dir, "good")
            good_files = sorted([
                f for f in os.listdir(good_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
            ]) if os.path.isdir(good_dir) else []

            total_defect_cats = [
                d for d in os.listdir(test_dir)
                if d != "good" and os.path.isdir(os.path.join(test_dir, d))
            ]
            total_files = len(good_files) + sum(
                len([f for f in os.listdir(os.path.join(test_dir, c))
                     if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))])
                for c in total_defect_cats
            )
            done = 0

            for fname in good_files:
                img = Image.open(os.path.join(good_dir, fname)).convert("RGB")
                score = model._image_score(img)
                all_scores.append(score)
                all_labels.append(0)
                done += 1
                q.put({"type": "progress", "done": done, "total": total_files,
                       "category": "good", "label": 0, "score": round(score, 4)})

            for cat in sorted(total_defect_cats):
                cat_dir = os.path.join(test_dir, cat)
                files = sorted([
                    f for f in os.listdir(cat_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
                ])
                cat_scores = []
                for fname in files:
                    img = Image.open(os.path.join(cat_dir, fname)).convert("RGB")
                    score = model._image_score(img)
                    all_scores.append(score)
                    all_labels.append(1)
                    cat_scores.append(score)
                    done += 1
                    q.put({"type": "progress", "done": done, "total": total_files,
                           "category": cat, "label": 1, "score": round(score, 4)})
                detected = sum(s > model.threshold for s in cat_scores)
                category_results.append({"name": cat, "total": len(files), "detected": detected})

            auroc = roc_auc_score(all_labels, all_scores)
            normal_total = all_labels.count(0)
            defect_total = all_labels.count(1)
            normal_pass = sum(s <= model.threshold for s, l in zip(all_scores, all_labels) if l == 0)
            defect_detected = sum(s > model.threshold for s, l in zip(all_scores, all_labels) if l == 1)

            q.put({
                "type": "done",
                "auroc": round(auroc, 4),
                "normal_total": normal_total,
                "normal_pass": normal_pass,
                "defect_total": defect_total,
                "defect_detected": defect_detected,
                "threshold": round(model.threshold, 4),
                "categories": category_results,
                "scores": [round(s, 4) for s in all_scores],
                "labels": all_labels,
            })
        except Exception as e:
            q.put({"type": "error", "message": str(e)})

    threading.Thread(target=do_benchmark, daemon=True).start()

    def generate():
        while True:
            item = q.get()
            yield f"data: {json.dumps(item)}\n\n"
            if item["type"] in ("done", "error"):
                break

    return StreamingResponse(generate(), media_type="text/event-stream")


app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
