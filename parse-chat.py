import os
import re
import csv
from collections import defaultdict


def parse_chat_file(input_file_path):
    # define the players (by LinkedIn display name),
    # their corresponding graph display names,
    # and their order on the graph.
    player_map = {
        "Josiah Plett": "Josiah",
        "Bob McBobbins": "Bobby",
        # ...
    }

    # dynamically generate columns from player_map
    columns = ["Day"] + list(player_map.values())

    data = defaultdict(lambda: {col: "-1" for col in columns[1:]})

    day_pattern = re.compile(r"Queens #(\d+)")
    sender_pattern = re.compile(r"^(.*) sent the following message")
    inline_time_pattern = re.compile(r"Queens #\d+(?: \|)?\s*(\d{1,2}:\d{2})")

    current_sender = None

    def convert_to_seconds(time_str):
        """Converts a time string in the format mm:ss to total seconds."""
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds

    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # check if the line indicates a new sender
                sender_match = sender_pattern.search(line)
                if sender_match:
                    sender_name_line = sender_match.group(1).strip()
                    if sender_name_line in player_map:
                        current_sender = player_map[sender_name_line]
                    continue

                if line in player_map:
                    current_sender = player_map[line]
                    continue

                # check for a day entry and time pattern in one step
                day_match = day_pattern.search(line)
                time_match = inline_time_pattern.search(line)

                if day_match and time_match and current_sender:
                    day_number = int(day_match.group(1))
                    time_value = time_match.group(1)
                    time_in_seconds = convert_to_seconds(time_value)
                    data[day_number]["Day"] = day_number
                    data[day_number][current_sender] = time_in_seconds
                    continue

                # additional check for multiline format, where time might be on the next line
                if day_match:
                    day_number = int(day_match.group(1))
                    data[day_number]["Day"] = day_number
                    continue

                # check if the line contains only a time pattern (for when time is on a new line)
                if time_pattern := re.match(r"^(\d{1,2}:\d{2})", line):
                    if day_number and current_sender:
                        time_value = time_pattern.group(1)
                        time_in_seconds = convert_to_seconds(time_value)
                        data[day_number][current_sender] = time_in_seconds
                        day_number = None
                    continue

    except FileNotFoundError:
        print(f"Error: The file {input_file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

    return data, columns


def fill_missing_days(data, columns):
    all_days = sorted(data.keys())
    if not all_days:
        return []

    min_day = all_days[0]
    max_day = all_days[-1]

    # ensure there's no missing days in the chart
    filled_data = []
    for day in range(min_day, max_day + 1):
        if day in data:
            filled_data.append(data[day])
        else:
            empty_day = {"Day": day}
            empty_day.update({col: "-1" for col in columns[1:]})
            filled_data.append(empty_day)

    return filled_data


def write_csv(data, columns, output_file_path):
    # fill in missing days (might make this an option eventually)
    filled_data = fill_missing_days(data, columns)

    try:
        with open(output_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()

            for row in filled_data:
                writer.writerow(row)

        print(f"Data successfully parsed and written to {output_file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


# Copyright Josiah Plett 2024


def main():
    input_file_path = "data/full-chat.txt"
    output_file_path = "data/queens-times.csv"

    # check if the input file exists
    if not os.path.exists(input_file_path):
        print(
            f"Error: Looks like {input_file_path} was deleted. Please ensure the file exists."
        )
        return

    data, columns = parse_chat_file(input_file_path)
    if data:
        write_csv(data, columns, output_file_path)


if __name__ == "__main__":
    main()
