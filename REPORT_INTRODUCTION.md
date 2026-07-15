# bits for the IEEE report

Copy/paste from here into the report and tweak the numbers once training is done.

---

## Research questions (put these near the top of intro)

**RQ1:** Can machine learning classify network traffic as benign or malicious on the CICIDS 2017 dataset?

**RQ2:** Which model gives the best balance between detection quality (precision, recall, F1) and how fast it runs on AWS (latency / throughput)?

How we picked "best": highest F1 on test set. If two models are within ~0.01 F1 we take the faster one.

---

## Introduction draft (3 paragraphs-ish)

Network attacks like DDoS and port scanning are a real problem for cloud providers. Normal IDS systems use fixed rules but attackers keep changing tactics. Machine learning might work better because it learns from examples — thats basically what we wanted to test.

We built CloudGuard-IDS for our H9CML project. We used the public CICIDS 2017 dataset (network flow records labelled benign or attack). Each of us trained a different classifier — Random Forest, SVM, neural network, gradient boosting — plus logistic regression as a baseline. Everyone used the same cleaned data and same test set so the comparison is fair. We generated comparison charts, error analysis heatmaps, and learning curves (models retrained on subsets of the training data). For cloud deployment we stored artefacts on S3, ran the same Flask demo UI locally and on Elastic Beanstalk, and exposed a Lambda + API Gateway `/predict` endpoint so we can compare serverless latency with a web-server deployment.

RQ1 is basically "does this even work?" and RQ2 is "ok but which one would you actually deploy on AWS?". We think the tree models will score higher on F1 but the simpler ones might be quicker. The results section will show which trade-off makes sense — and the AWS section will note that Elastic Beanstalk hosts the interactive Flask demo while Lambda is a lightweight inference API for comparison.

---

## Abstract one-liner

We trained four classifiers and a logistic regression baseline on CICIDS 2017 for intrusion detection and compared them on F1 and inference latency, deploying a shared Flask UI on Elastic Beanstalk and a Lambda prediction API on AWS.

---

## Deployment note (for methodology / cloud section)

- **Train locally**, deploy inference only.
- **S3** holds models and report images.
- **Elastic Beanstalk** runs Flask + gunicorn (same `application.py` as `run_demo.py` locally) with metrics, plots, learning curves, and a predict form.
- **Lambda + API Gateway** offers `GET /predict` (health) and `POST /predict` (classification); default packaged model is logistic regression to stay under Lambda size limits.
- Learning-curve F1 scores sit near 0.99+ for the strong tree models, so plots use a zoomed y-axis so differences are visible.

---

## Ethics (stick this somewhere in methodology or intro)

CICIDS is from a lab testbed not real user traffic so theres no personal data. Still, if you deployed this for real, false positives would annoy people and false negatives are obviously bad. Worth mentioning in limitations.
