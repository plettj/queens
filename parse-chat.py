import os
import re
import csv
from collections import defaultdict

# Copyright Josiah Plett 2024


def parse_chat_file(input_file_path):
    # Define the column order
    columns = [
        "Day",
        "Adrien",
        "Josiah",
        "Ben",
        "Marshall",
        "Justin",
        "Nicole",
        "Alex",
    ]

    # Initialize data structure
    data = defaultdict(lambda: {col: "-1" for col in columns[1:]})

    # Regex patterns
    day_pattern = re.compile(r"Queens #(\d+)")
    sender_pattern = re.compile(r"^(.*) sent the following message")
    # This regex looks for time directly after "Queens #" entries
    inline_time_pattern = re.compile(r"Queens #\d+(?: \|)?\s*(\d{1,2}:\d{2})")

    current_sender = None

    sender_map = {
        "Adrien Fraser": "Adrien",
        "Josiah Plett": "Josiah",
        "Ben DePetris": "Ben",
        "Marshall Cowie": "Marshall",
        "Justin Zwart": "Justin",
        "Nicole Planeta": "Nicole",
        "Alex Fraser": "Alex",
    }

    def convert_to_seconds(time_str):
        """Converts a time string in the format mm:ss to total seconds."""
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds

    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Check if the line indicates a new sender
                sender_match = sender_pattern.search(line)
                if sender_match:
                    sender_name_line = sender_match.group(1).strip()
                    if sender_name_line in sender_map:
                        current_sender = sender_map[sender_name_line]
                    continue

                # Update current sender if it matches a profile view line
                if line in sender_map:
                    current_sender = sender_map[line]
                    continue

                # Check for a day entry and time pattern in one step
                day_match = day_pattern.search(line)
                time_match = inline_time_pattern.search(line)

                if day_match and time_match and current_sender:
                    day_number = int(day_match.group(1))
                    time_value = time_match.group(1)
                    # Convert time to total seconds
                    time_in_seconds = convert_to_seconds(time_value)

                    # Use only the day number as the key
                    data[day_number]["Day"] = day_number
                    data[day_number][current_sender] = time_in_seconds
                    continue  # Move to the next line after finding a day and time

                # Additional check for multiline format, where time might be on the next line
                if day_match:
                    # Extract day number and prepare the day_key
                    day_number = int(day_match.group(1))
                    data[day_number]["Day"] = day_number
                    continue

                # Check if the line contains only a time pattern (used for cases where time is on a new line)
                if time_pattern := re.match(r"^(\d{1,2}:\d{2})", line):
                    if day_number and current_sender:
                        # Use previously captured day_number and current_sender for this time
                        time_value = time_pattern.group(1)
                        time_in_seconds = convert_to_seconds(time_value)
                        data[day_number][current_sender] = time_in_seconds
                        day_number = None  # Reset after use to avoid misassignment
                    continue

    except FileNotFoundError:
        print(f"Error: The file {input_file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

    return data, columns


def fill_missing_days(data, columns):
    # Find the range of days
    all_days = sorted(data.keys())
    if not all_days:
        return []

    min_day = all_days[0]
    max_day = all_days[-1]

    # Ensure all days from min_day to max_day are present
    filled_data = []
    for day in range(min_day, max_day + 1):
        if day in data:
            filled_data.append(data[day])
        else:
            # Fill missing day with default "-1" values
            empty_day = {"Day": day}
            empty_day.update({col: "-1" for col in columns[1:]})
            filled_data.append(empty_day)

    return filled_data


def write_csv(data, columns, output_file_path):
    # Fill in missing days
    filled_data = fill_missing_days(data, columns)

    # Sort and write to CSV
    try:
        with open(output_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()

            for row in filled_data:
                writer.writerow(row)

        print(f"Data successfully parsed and written to {output_file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def main():
    # Construct the full paths to the input and output files
    input_file_path = "data/full-chat.txt"
    output_file_path = "data/queens-times.csv"

    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print(f"Error: The input file was not found at {input_file_path}")
        return

    data, columns = parse_chat_file(input_file_path)
    if data:
        write_csv(data, columns, output_file_path)


if __name__ == "__main__":
    main()
