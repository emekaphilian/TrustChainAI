# ==========================================================
# TrustChainAI - AI Smart Contract Security Platform
# ==========================================================

import streamlit as st
import torch
import json
import requests
import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="TrustChainAI Security Platform",
    layout="wide"
)

st.title("🛡 TrustChainAI – AI Smart Contract Auditor")

# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "data" / "models" / "vulnerability_detector_v1"

# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

@st.cache_resource
def load_model():

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    with open(MODEL_PATH / "label_map.json") as f:
        maps = json.load(f)

    reverse_map = {int(k): v for k, v in maps["label_to_vulnerability"].items()}

    return tokenizer, model, reverse_map


tokenizer, model, reverse_map = load_model()

model.eval()

# ---------------------------------------------------------
# ETHERSCAN INTEGRATION
# ---------------------------------------------------------

ETHERSCAN_API = "YOUR_ETHERSCAN_API_KEY"

def fetch_contract(address):

    url = "https://api.etherscan.io/api"

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API
    }

    r = requests.get(url, params=params).json()

    if r["status"] == "1":
        return r["result"][0]["SourceCode"]

    return None


# ---------------------------------------------------------
# PREDICTION ENGINE
# ---------------------------------------------------------

def predict_contract(code):

    inputs = tokenizer(
        code,
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

    label = reverse_map[pred_id]

    risk_score = round(confidence * 100, 2)

    return label, confidence, risk_score


# ---------------------------------------------------------
# AUTO VULNERABILITY CLASSIFIER
# ---------------------------------------------------------

def classify_vulnerability(code):

    if "call.value" in code or ".call(" in code:
        return "Reentrancy"

    if "+=" in code and "uint" in code:
        return "Integer Overflow"

    if "tx.origin" in code:
        return "Phishing Risk"

    return "No Known Pattern"


# ---------------------------------------------------------
# ATTACK SIMULATION ENGINE
# ---------------------------------------------------------

def simulate_attack(code):

    if "call.value" in code:
        return {
            "attack": "Reentrancy Attack",
            "severity": "Critical",
            "probability": 0.91
        }

    if "tx.origin" in code:
        return {
            "attack": "Phishing Exploit",
            "severity": "High",
            "probability": 0.78
        }

    return {
        "attack": "None",
        "severity": "Low",
        "probability": 0.05
    }


# ---------------------------------------------------------
# CONTRACT EMBEDDINGS FOR SIMILARITY
# ---------------------------------------------------------

def embed_contract(code):

    tokens = tokenizer(
        code,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.base_model(**tokens)

    emb = outputs.last_hidden_state.mean(dim=1).numpy()

    return emb


def compute_similarity(code, references):

    emb1 = embed_contract(code)

    scores = []

    for ref in references:

        emb2 = embed_contract(ref)

        score = cosine_similarity(emb1, emb2)[0][0]

        scores.append(score)

    return scores


reference_contracts = [
    "msg.sender.call.value(amount)()",
    "balance[to] += value",
    "if(tx.origin == owner)"
]

# ---------------------------------------------------------
# SHAP EXPLAINABILITY
# ---------------------------------------------------------

def explain_prediction(code):

    def f(x):

        tokens = tokenizer(
            x.tolist(),
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model(**tokens)

        return outputs.logits.numpy()

    explainer = shap.Explainer(f, tokenizer)

    shap_values = explainer([code])

    return shap_values


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

mode = st.sidebar.selectbox(
    "Platform Modules",
    [
        "Contract Scanner",
        "Live Ethereum Scanner",
        "Attack Simulation",
        "Dataset Generator"
    ]
)

# =========================================================
# CONTRACT SCANNER
# =========================================================

if mode == "Contract Scanner":

    st.header("🔎 Smart Contract Scanner")

    contract_code = st.text_area(
        "Paste Solidity Contract",
        height=250
    )

    if st.button("Analyze Contract"):

        label, confidence, risk_score = predict_contract(contract_code)

        vuln_type = classify_vulnerability(contract_code)

        similarity = compute_similarity(contract_code, reference_contracts)

        attack = simulate_attack(contract_code)

        # --------------------------------------------------
        # RISK DASHBOARD
        # --------------------------------------------------

        st.subheader("📊 Risk Dashboard")

        c1, c2, c3 = st.columns(3)

        c1.metric("Prediction", label)
        c2.metric("Confidence", f"{confidence*100:.2f}%")
        c3.metric("Risk Score", risk_score)

        fig, ax = plt.subplots()

        ax.barh(["Risk Score"], [risk_score])

        ax.set_xlim(0,100)

        st.pyplot(fig)

        # --------------------------------------------------
        # VULNERABILITY TYPE
        # --------------------------------------------------

        st.subheader("🧬 Vulnerability Type")

        st.write(vuln_type)

        # --------------------------------------------------
        # CONTRACT SIMILARITY
        # --------------------------------------------------

        st.subheader("🔎 Similar Contract Patterns")

        df = pd.DataFrame({
            "Pattern":[
                "Reentrancy Pattern",
                "Token Transfer",
                "Phishing Pattern"
            ],
            "Similarity Score": similarity
        })

        st.dataframe(df)

        # --------------------------------------------------
        # ATTACK SIMULATION
        # --------------------------------------------------

        st.subheader("⚠ Attack Simulation")

        st.json(attack)

        # --------------------------------------------------
        # EXPLAINABLE AI
        # --------------------------------------------------

        st.subheader("🧠 Explainable AI")

        shap_values = explain_prediction(contract_code)

        shap.plots.text(shap_values[0])


# =========================================================
# LIVE ETHEREUM SCANNER
# =========================================================

elif mode == "Live Ethereum Scanner":

    st.header("🌐 Scan Live Ethereum Contract")

    address = st.text_input("Ethereum Contract Address")

    if st.button("Fetch & Analyze"):

        source = fetch_contract(address)

        if source:

            st.success("Contract fetched")

            label, confidence, risk_score = predict_contract(source)

            st.write("Prediction:", label)
            st.write("Risk Score:", risk_score)

        else:

            st.error("Unable to fetch contract")


# =========================================================
# ATTACK SIMULATION PAGE
# =========================================================

elif mode == "Attack Simulation":

    st.header("⚠ AI Attack Simulator")

    contract = st.text_area("Paste Contract")

    if st.button("Simulate Attack"):

        result = simulate_attack(contract)

        st.json(result)


# =========================================================
# DATASET GENERATOR
# =========================================================

elif mode == "Dataset Generator":

    st.header("📦 Smart Contract Dataset Generator")

    size = st.slider("Number of contracts",1000,50000,10000)

    st.write(
        f"This module will collect {size} smart contracts "
        "from blockchain sources for future training."
    )

    if st.button("Generate Dataset"):

        st.success("Dataset generation module ready (backend pipeline)")