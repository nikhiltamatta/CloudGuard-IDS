# preprocessing script - run once at the start
# loads all 8 csvs, cleans them, splits train/val/test

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

import config


def read_file(path):
    # had to use latin-1 or pandas throws encoding errors on some rows
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    df.columns = df.columns.str.strip()  # headers have random spaces sometimes
    return df


def clean(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    df = df.drop_duplicates()

    df["Label"] = df["Label"].astype(str).str.strip()
    df["attack_type"] = df["Label"]  # keep original name for error analysis later
    df["label"] = (df["Label"] != "BENIGN").astype(int)  # 0=ok, 1=attack
    return df


def main():
    print("Loading csv files...")
    frames = []

    for filename in config.CICIDS_FILES:
        path = config.RAW_DATA_DIR / filename
        if not path.exists():
            print(f"cant find {path}")
            print("put the csv files in dataset/ folder first")
            return
        print(f"  {filename}")
        frames.append(clean(read_file(path)))

    data = pd.concat(frames, ignore_index=True)
    print(f"rows after clean: {len(data):,}")
    print(data["label"].value_counts())  # should be mostly benign

    features = data.drop(columns=["Label", "attack_type", "label"])

    # some columns come in as strings for some reason
    for col in features.columns:
        if features[col].dtype == object:
            features[col] = pd.to_numeric(features[col], errors="coerce")

    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.dropna(axis=1, how="any")  # drop cols that still have nans

    labels = data.loc[features.index, "label"]
    attacks = data.loc[features.index, "attack_type"]

    # 70 train, rest split into val + test
    x_train, x_temp, y_train, y_temp, a_train, a_temp = train_test_split(
        features, labels, attacks,
        test_size=config.VAL_SIZE + config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=labels,
    )

    val_ratio = config.VAL_SIZE / (config.VAL_SIZE + config.TEST_SIZE)
    x_val, x_test, y_val, y_test, a_val, a_test = train_test_split(
        x_temp, y_temp, a_temp,
        test_size=1 - val_ratio,
        random_state=config.RANDOM_STATE,
        stratify=y_temp,
    )

    # scaling - some features are huge numbers (bytes, durations etc)
    scaler = RobustScaler()
    x_train = pd.DataFrame(scaler.fit_transform(x_train), columns=features.columns)
    x_val = pd.DataFrame(scaler.transform(x_val), columns=features.columns)
    x_test = pd.DataFrame(scaler.transform(x_test), columns=features.columns)

    out = config.DATA_DIR
    out.mkdir(parents=True, exist_ok=True)

    x_train.to_csv(out / "x_train.csv", index=False)
    x_val.to_csv(out / "x_val.csv", index=False)
    x_test.to_csv(out / "x_test.csv", index=False)
    y_train.to_frame("label").to_csv(out / "y_train.csv", index=False)
    y_val.to_frame("label").to_csv(out / "y_val.csv", index=False)
    y_test.to_frame("label").to_csv(out / "y_test.csv", index=False)
    a_test.to_frame("attack_type").to_csv(out / "attack_type_test.csv", index=False)
    pd.Series(features.columns).to_csv(out / "feature_columns.csv", index=False, header=["feature"])
    joblib.dump(scaler, out / "scaler.joblib")

    print(f"\nsaved to {out}")
    print(f"train {len(x_train):,} | val {len(x_val):,} | test {len(x_test):,}")


if __name__ == "__main__":
    main()
