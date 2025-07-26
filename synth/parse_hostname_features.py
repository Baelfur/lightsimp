import os
import pandas as pd
from shared.constants import (
    DEVICE_ROLE_CODES,
    REGION_SITE_MAP
)

# --- Dynamic path setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILE = os.path.join(DATA_DIR, "labeled_asset_dataset.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "labeled_asset_dataset_enriched.csv")

# Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Reverse role code map: ED → edge
ROLE_CODE_TO_NAME = {v: k for k, v in DEVICE_ROLE_CODES.items()}

# Reverse site → region map: DAL → central
SITE_TO_REGION = {
    site: region
    for region, sites in REGION_SITE_MAP.items()
    for site in sites
}

# Load data
df = pd.read_csv(INPUT_FILE)

# Extract structured elements from hostname
df["site_code"] = df["hostname"].str[0:3]
df["state_code"] = df["hostname"].str[3:5]
df["role_code"] = df["hostname"].str[5:7]

# Map to higher-level attributes
df["parsed_role"] = df["role_code"].map(ROLE_CODE_TO_NAME)
df["parsed_region"] = df["site_code"].map(SITE_TO_REGION)

# Save enriched file
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Enriched dataset with parsed features written to: {OUTPUT_FILE}")
