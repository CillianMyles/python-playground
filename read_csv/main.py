import csv

def main():
    with open("all.csv", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            print(f"{[len(row)]} {row}")

main()
