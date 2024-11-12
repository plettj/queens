import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def load_data(file_path):
    return pd.read_csv(file_path)


def save_plot(fig, save_directory="output", filename="queens_times_plot.png"):
    os.makedirs(save_directory, exist_ok=True)

    file_path = os.path.join(save_directory, filename)

    # save with a *transparent* background
    fig.savefig(file_path, transparent=True, dpi=300)
    print(f"Plot saved to {file_path}")


def calculate_stats(data):
    stats = {}
    global_times = data.copy()

    # fastest time globally
    fastest_time, fastest_person, fastest_day = float("inf"), None, None
    for person in global_times.columns[1:]:
        for day, time in zip(global_times["Day"], global_times[person]):
            if time != -1:
                if time < fastest_time:
                    fastest_time, fastest_person, fastest_day = time, person, day

    if fastest_person:
        stats["Fastest time"] = {
            "person": fastest_person,
            "time": fastest_time,
            "day": fastest_day,
        }

    # fastest overall average
    avg_times = {
        person: global_times[person][global_times[person] != -1].mean()
        for person in global_times.columns[1:]
    }
    fastest_avg_person = min(avg_times, key=avg_times.get)
    stats["Fastest overall average"] = {
        "person": fastest_avg_person,
        "average": avg_times[fastest_avg_person],
    }

    # fastest average-of-5 (must be consecutive)
    min_rolling_avg, min_rolling_person, min_rolling_day = float("inf"), None, None
    for person, times in global_times.drop(columns="Day").items():
        rolling_avg = times.replace(-1, np.nan).rolling(window=5).mean().dropna()
        if not rolling_avg.empty:
            person_min_avg = rolling_avg.min()
            if person_min_avg < min_rolling_avg:
                min_rolling_avg = person_min_avg
                min_rolling_person = person
                min_rolling_day = global_times["Day"].iloc[rolling_avg.idxmin()]

    if min_rolling_person:
        stats["Fastest average of 5"] = {
            "person": min_rolling_person,
            "average": min_rolling_avg,
            "day": min_rolling_day,
        }

    # longest unbroken streak
    max_streak, streak_person, start_day = 0, None, 0
    for person in global_times.columns[1:]:
        longest_streak, current_streak, end_day = 0, 0, 0
        for day, time in zip(global_times["Day"], global_times[person]):
            if time != -1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
                end_day = day
            else:
                current_streak = 0
        if longest_streak > max_streak:
            max_streak, streak_person, start_day = (
                longest_streak,
                person,
                end_day - longest_streak + 1,
            )
    stats["Longest streak"] = {
        "person": streak_person,
        "streak": max_streak,
        "day": start_day,
    }

    return stats


def plot_data(data, stats):
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.subplots_adjust(right=0.7)

    # get the color of each person in the plot
    colors = {}
    lines = []
    for person in data.columns[1:]:
        days = data["Day"]
        times = data[person].apply(lambda x: x if x != -1 else np.nan)
        (line,) = ax.plot(
            days, times, label=person, marker="o", linestyle="-", markersize=5
        )
        colors[person] = line.get_color()
        lines.append(line)

    max_time = data.iloc[:, 1:].replace(-1, np.nan).max().max()
    max_time = (int((max_time // 60 + 1) * 60)) if not np.isnan(max_time) else 60

    # add horizontal lines for minute intervals
    for minute in range(60, max_time + 60, 60):
        plt.axhline(minute, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)

    plt.ylim(bottom=0)

    plt.xlabel("Day")
    plt.ylabel("Time (seconds)")
    plt.title("Queens Times Over Time")
    plt.legend(handles=lines, loc="upper right", bbox_to_anchor=(1.3, 1))

    # display global stats on the plot in the right margin with color-coded text!
    x_pos = 0.78
    y_pos = 0.7 - len(data.columns) * 0.015
    for key, value in stats.items():
        person_color = colors.get(value.get("person"), "black")

        # display the title in bold
        plt.gcf().text(
            x_pos,
            y_pos,
            f"{key}:",
            fontsize=10,
            weight="bold",
            color="black",
            ha="left",
            va="top",
            transform=plt.gcf().transFigure,
        )
        y_pos -= 0.03

        # display the details in the person's color
        if "time" in value:
            detail_text = f"{value['person']} - {value['time']}s, Day: {value['day']}"
        elif "average" in value:
            detail_text = f"{value['person']} - {value['average']:.2f}s"
        elif "streak" in value:
            detail_text = (
                f"{value['person']} - {value['streak']} day{"s" if value['streak'] > 1 else ""}, Start Day: {value['day']}"
            )

        plt.gcf().text(
            x_pos + 0.02,
            y_pos,
            detail_text,
            fontsize=10,
            color=person_color,
            ha="left",
            va="top",
            transform=plt.gcf().transFigure,
        )
        y_pos -= 0.05

    plt.show()

    # Save the *transparent* plot into the graphs directory
    save_plot(fig, save_directory="graphs", filename="transparent_plot.png")


# Copyright Josiah Plett 2024


def main():
    file_path = "data/queens-times.csv"
    data = load_data(file_path)
    stats = calculate_stats(data)
    plot_data(data, stats)


if __name__ == "__main__":
    main()
