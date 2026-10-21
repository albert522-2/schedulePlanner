# schedulePlanner
A Python scheduling app built with CMU Graphics. (15-112 Mini Project)

The app follows the Model-View-Controller pattern. The backend considers tasks in deadline order and removes tasks with the lowest weight-per-hour ratio when time is insufficient. A second pass reconsiders deferred tasks to fill remaining usable time.

Note that this is a greedy scheduling algorithm, so it does not guarantee the mathematically optimal schedule.

## Features

- Add tasks with a name, description, duration, deadline, and priority.
- Generate a schedule based on available hours.
- View scheduled and deferred tasks.
- Delete tasks and automatically refresh the schedule.
- See deadline urgency through red, yellow, and green indicators.

## Running the App

Install Python 3 and the `cmu_graphics` package, then run:

    python3 main.py

## How to Use

1. Set your available work hours.
2. Click **Add task** and enter the task details.
3. Enter deadlines as whole hours from now and durations in hours.
4. Use priority position 1 for the highest priority.
5. Review the schedule, navigate between pages, or click **X** to delete a task.
