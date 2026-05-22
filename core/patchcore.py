import os
import pickle
from typing import Callable

import cv2
import numpy as np
import torch
from PIL import Image
from scipy.ndimage import gaussian_filter
from sklearn.neighbors import NearestNeighbors

from core.extractor import FeatureExtractor


class PatchCore:
    def __init__(self, extractor: FeatureExtractor, n_neighbors: int = 9):
        self.extractor = extractor
        self.n_neighbors = n_neighbors
        self.memory_bank: np.ndarray | None = None
        self.threshold: float | None = None
        self._nbrs: NearestNeighbors | None = None
        self._memory_tensor: torch.Tensor | None = None

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, image_dir: str, callback: Callable | None = None) -> int:
        files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        ])
        total = len(files)

        all_patches = []
        for i, fname in enumerate(files):
            img = Image.open(os.path.join(image_dir, fname)).convert("RGB")
            patches, _ = self.extractor.extract(img)
            all_patches.append(patches)
            if callback:
                callback(i + 1, total)

        self.memory_bank = np.concatenate(all_patches, axis=0)
        self._build_index()
        self.threshold = None
        return total

    def calibrate(self, image_dir: str, callback: Callable | None = None) -> tuple[float, list[float]]:
        """Score held-out normal images and set threshold at 99th percentile."""
        files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        ])
        total = len(files)
        scores = []

        for i, fname in enumerate(files):
            img = Image.open(os.path.join(image_dir, fname)).convert("RGB")
            scores.append(self._image_score(img))
            if callback:
                callback(i + 1, total, scores[-1])

        self.threshold = float(np.percentile(scores, 99))
        return self.threshold, scores

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------

    def predict(self, image: Image.Image) -> dict:
        score, anomaly_map = self._score_map(image)
        heatmap_bgr = self._to_heatmap(image, anomaly_map)

        return {
            "score": round(score, 4),
            "is_defect": score > (self.threshold or 0.0),
            "threshold": round(self.threshold or 0.0, 4),
            "heatmap_bgr": heatmap_bgr,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump({
                "memory_bank": self.memory_bank,
                "threshold": self.threshold,
                "n_neighbors": self.n_neighbors,
            }, f)

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.memory_bank = data["memory_bank"]
        self.threshold = data["threshold"]
        self.n_neighbors = data["n_neighbors"]
        self._build_index()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_index(self) -> None:
        if self.extractor.device == "cuda":
            self._memory_tensor = torch.from_numpy(self.memory_bank).float().cuda()
            self._nbrs = None
        else:
            self._nbrs = NearestNeighbors(n_neighbors=self.n_neighbors, metric="euclidean", n_jobs=-1)
            self._nbrs.fit(self.memory_bank)
            self._memory_tensor = None

    def _knn_distances(self, patches: np.ndarray) -> np.ndarray:
        if self._memory_tensor is not None:
            q = torch.from_numpy(patches).float().cuda()
            dists = torch.cdist(q.unsqueeze(0), self._memory_tensor.unsqueeze(0)).squeeze(0)
            return dists.topk(self.n_neighbors, largest=False, dim=1).values.mean(dim=1).cpu().numpy()
        else:
            return self._nbrs.kneighbors(patches)[0].mean(axis=1)

    def _image_score(self, image: Image.Image) -> float:
        score, _ = self._score_map(image)
        return score

    def _score_map(self, image: Image.Image) -> tuple[float, np.ndarray]:
        patches, (h, w) = self.extractor.extract(image)
        patch_scores = self._knn_distances(patches).reshape(h, w)

        orig_w, orig_h = image.size
        score_map = cv2.resize(patch_scores, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        score_map = gaussian_filter(score_map, sigma=4)

        return float(score_map.max()), score_map

    def _to_heatmap(self, image: Image.Image, score_map: np.ndarray) -> np.ndarray:
        norm = (score_map - score_map.min()) / (score_map.max() - score_map.min() + 1e-8)
        heatmap = cv2.applyColorMap((norm * 255).astype(np.uint8), cv2.COLORMAP_JET)
        orig_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return cv2.addWeighted(orig_bgr, 0.6, heatmap, 0.4, 0)
