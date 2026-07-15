# Dataset folder

Put the 8 CICIDS 2017 csv files here before running `preprocess.py`.

Download from the Canadian Institute for Cybersecurity (search "CICIDS 2017").

Files needed:
- Monday-WorkingHours.pcap_ISCX.csv
- Tuesday-WorkingHours.pcap_ISCX.csv
- Wednesday-workingHours.pcap_ISCX.csv
- Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
- Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
- Friday-WorkingHours-Morning.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv

We dont upload the csvs to github cause some files are over 100mb.

After preprocess, trained models and charts live under `data/processed/` and `models/` — those feed the **Flask** demo (`python3 run_demo.py`) and the AWS deploy (`upload_s3.sh` / Elastic Beanstalk). You do **not** need the raw CSVs on Elastic Beanstalk; only the processed feature list + saved models + report PNGs.
