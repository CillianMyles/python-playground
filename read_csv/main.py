import csv
import pandas as pd

def main():
    print_block("STD")
    read_csv_std()
    print_block("PANDAS")
    read_csv_pandas()

def print_block(text):
    print(f"====== {text} ======")

def read_csv_std():
    with open("all.csv", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            print(f"{[len(row)]} {row}")

def read_csv_pandas():
    df = pd.read_csv("all.csv")
    for _, row in df.iterrows():
        values = row.tolist()
        print(f"[{len(values)}] {values}")

main()
