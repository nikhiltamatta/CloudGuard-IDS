# config stuff for the whole project
# change paths here if your folder layout is different

import os
from pathlib import Path

ROOT = Path(__file__).parent

# raw csvs from CICIDS 2017
RAW_DATA_DIR = ROOT / "dataset"

# created by preprocess.py
DATA_DIR = ROOT / "data" / "processed"

# each model saves here after training
MODELS_DIR = ROOT / "models"

# 70/15/15 split - lecturer said stratified split is fine
TRAIN_SIZE = 0.70
VAL_SIZE = 0.15
TEST_SIZE = 0.15
RANDOM_STATE = 42  # keep it 42 so results are reproducible

# for learning curve script
SUBSET_SIZES = [0.10, 0.25, 0.50, 1.00]

# TODO: change bucket name before uploading to s3
# EB sets S3_BUCKET as an environment variable at runtime
S3_BUCKET = os.environ.get("S3_BUCKET", "cloudguard-ids-nikhil-341757264632")

# filenames from the dataset download
CICIDS_FILES = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
]
