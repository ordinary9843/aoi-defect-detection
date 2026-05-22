import numpy as np
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image


class FeatureExtractor:
    def __init__(self, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._features: dict = {}

        self.model = models.wide_resnet50_2(weights=models.Wide_ResNet50_2_Weights.IMAGENET1K_V1)
        self.model.eval().to(self.device)

        self.model.layer2.register_forward_hook(self._hook("layer2"))
        self.model.layer3.register_forward_hook(self._hook("layer3"))

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def _hook(self, name: str):
        def fn(_, __, output):
            self._features[name] = output
        return fn

    def extract(self, image: Image.Image) -> tuple[np.ndarray, tuple[int, int]]:
        """Return (patch_features, (h, w)) where patch_features is (h*w, C)."""
        x = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            self.model(x)

        f2 = self._features["layer2"]  # (1, 512, 28, 28)
        f3 = self._features["layer3"]  # (1, 1024, 14, 14)

        f3_up = F.interpolate(f3, size=f2.shape[2:], mode="bilinear", align_corners=False)
        features = torch.cat([f2, f3_up], dim=1)  # (1, 1536, 28, 28)

        _, c, h, w = features.shape
        patches = features.permute(0, 2, 3, 1).reshape(h * w, c)

        return patches.cpu().numpy(), (h, w)
