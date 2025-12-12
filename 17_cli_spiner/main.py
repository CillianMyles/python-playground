import time
from spinner import spinning

_visible_for = 2.0  # seconds


MESSAGES = [
    "Reading input...",
    "Applying transformations to data...",
    "Generating output...",
    "Writing output...",
]


def main():
    with spinning() as spinner:
        for message in MESSAGES:
            spinner.message = message
            time.sleep(_visible_for)


if __name__ == "__main__":
    main()
