
import torch
import numpy as np
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path

MODEL_PATH = r"c:\Users\phili\Documents\Projects\TrustChainAi\data\models\vulnerability_detector_v1"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

with open(Path(MODEL_PATH) / "label_map.json") as f:
    maps = json.load(f)

reverse_map = {int(k): v for k, v in maps["label_to_vulnerability"].items()}


def scan_contract(contract_code):

    inputs = tokenizer(
        contract_code,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits.numpy()[0]

    probs = np.exp(logits) / np.sum(np.exp(logits))

    pred_id = int(np.argmax(probs))
    confidence = float(np.max(probs))

    vulnerability = reverse_map[pred_id]

    risk_score = round(confidence * 100, 2)

    return {
        "prediction": vulnerability,
        "confidence": confidence,
        "risk_score": risk_score
    }
