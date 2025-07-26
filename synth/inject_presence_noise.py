import os
import pandas as pd
import numpy as np

from shared.constants import (
    ROLE_VENDOR_MODEL_MAP,
    INVENTORY_MODEL_MISSING_PROBS,
    IPAM_REGION_MISSING_PROBS,
    DEFAULT_MODEL_FAILURE_PROB
)

# --- Dynamic path resolution ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILE = os.path.join(DATA_DIR, "base_asset_dataset.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "labeled_asset_dataset.csv")

# Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Load data ---
df = pd.read_csv(INPUT_FILE)

# --- Inject INVENTORY missing flags per model ---
df["missing_in_inventory"] = 0  # start with everything present

for model, failure_rate in INVENTORY_MODEL_MISSING_PROBS.items():
    idx = df["model"] == model
    n = idx.sum()
    n_fail = int(n * failure_rate)
    
    if n_fail > 0:
        fail_indices = df[idx].sample(n=n_fail, random_state=42).index
        df.loc[fail_indices, "missing_in_inventory"] = 1

# Ensure all models from ROLE_VENDOR_MODEL_MAP are represented
reference_models = set(model for models in ROLE_VENDOR_MODEL_MAP.values() for _, model in models)
for model in reference_models:
    if model not in INVENTORY_MODEL_MISSING_PROBS:
        print(f"⚠️ WARNING: Model {model} missing from INVENTORY_MODEL_FAILURE_PROBS. Using default {DEFAULT_MODEL_FAILURE_PROB}.")
        idx = df["model"] == model
        n = idx.sum()
        n_fail = int(n * DEFAULT_MODEL_FAILURE_PROB)
        if n_fail > 0:
            fail_indices = df[idx].sample(n=n_fail, random_state=42).index
            df.loc[fail_indices, "missing_in_inventory"] = 1

# --- Inject IPAM missing flags per region ---
df["missing_in_ipam"] = 0  # start with everything present

for region, failure_rate in IPAM_REGION_MISSING_PROBS.items():
    idx = df["region"] == region
    n = idx.sum()
    n_fail = int(n * failure_rate)

    if n_fail > 0:
        fail_indices = df[idx].sample(n=n_fail, random_state=42).index
        df.loc[fail_indices, "missing_in_ipam"] = 1

# --- Save the updated dataset ---
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Risk-labeled dataset written to: {OUTPUT_FILE}")
