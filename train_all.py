# runs everyones training scripts in order
# grab a snack, svm takes ages

import train_random_forest
import train_svm
import train_neural_network
import train_gradient_boosting
import train_logistic_regression


def main():
    print("=== training everything ===\n")

    print("[1/5] baseline")
    train_logistic_regression.train()

    print("[2/5] random forest (nikhil)")
    train_random_forest.train()

    print("[3/5] svm (ishan) -- slow warning")
    train_svm.train()

    print("[4/5] neural net (aman)")
    train_neural_network.train()

    print("[5/5] gradient boosting (ajay)")
    train_gradient_boosting.train()

    print("\nfinished. run compare_models.py next")


if __name__ == "__main__":
    main()
