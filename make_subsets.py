# smaller training sets for the learning curve part of the report
# run after preprocess.py

import pandas as pd
import config


def main():
    x_train = pd.read_csv(config.DATA_DIR / "x_train.csv")
    y_train = pd.read_csv(config.DATA_DIR / "y_train.csv")["label"]

    out = config.DATA_DIR / "subsets"
    out.mkdir(parents=True, exist_ok=True)

    for pct in config.SUBSET_SIZES:
        if pct >= 1.0:
            sample_x, sample_y = x_train, y_train
        else:
            sample_x = x_train.sample(frac=pct, random_state=config.RANDOM_STATE)
            sample_y = y_train.loc[sample_x.index]

        name = f"train_{int(pct * 100)}pct"
        sample_x.to_csv(out / f"{name}_x.csv", index=False)
        sample_y.to_frame("label").to_csv(out / f"{name}_y.csv", index=False)
        print(f"{name}: {len(sample_x):,} rows")


if __name__ == "__main__":
    main()
