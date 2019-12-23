import csv
import json
import logging

def parse_csv(csv_file):
    json_file = None
    try:
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        with open('file.json', 'w') as jf:
            json_file = json.dump(rows, jf)
            f.close()
            jf.close()

        return json_file

    except Exception as e:
        logging.error(f"Failing with error : {e}")

