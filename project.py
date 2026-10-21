from menu import main_menu
from ToolManager import ToolManager
from typing import Literal
import random
import json
import platform
import subprocess
import time
import csv
import os


def main():
    client, provider_name = main_menu()
    welcome_message = random.choice([
        "Just stopping by? ",
        "Where should we start? ",
        "Hi, what's on your mind? ",
        "The mic is yours: ",
        "Let's jump in, what do you want me to do? "
    ])
    prompt = input(welcome_message)
    match provider_name:
        case "gemini":
            interaction = client.interactions.create(
                model="gemini-2.5-flash",
                input=prompt,
                tools=ToolManager.to_gemini()
            )


    function_responses = []

    for step in interaction.steps:
        if step.type == "function_call":
            tool_response = ToolManager.execute(step.name, **step.arguments)
            
            function_responses.append({
                "type": "function_result",
                "name": step.name,                        
                "call_id": step.id,
                "result": json.dumps({"result": tool_response}) 
            })

    if function_responses:
        final_interaction = client.interactions.create(
            model="gemini-2.5-flash",
            previous_interaction_id=interaction.id,
            tools=ToolManager.to_gemini(),                 
            input=function_responses
        )
        print(final_interaction.output_text)
    else:
        print(interaction.output_text)


            
@ToolManager.register
def calculator(op: Literal['/', '+', '-', '*'], n1: float, n2: float) -> float:
    """Performs a basic arithmetic operation on two numeric values.

    Args:
        op: The arithmetic operator to apply. Must be one of:
            '+' (addition), '-' (subtraction), '*' (multiplication), or '/' (division).
        n1: The first operand (left-hand side number). In division, this represents the numerator (dividend).
        n2: The second operand (right-hand side number). In division, this represents the denominator (divisor, cannot be zero).

    Returns:
        float: The calculated mathematical result of applying the operation (n1 op n2).

    Raises:
        ValueError: If an unsupported operator is supplied.
        ZeroDivisionError: If division by zero is attempted when op is '/'.
    """
    match op:
        case "+":
            return n1 + n2
        case "-":
            return n1 - n2
        case "*":
            return n1 * n2
        case "/":
            if n2 == 0:
                raise ZeroDivisionError
            return n1 / n2
        case _:
            raise ValueError("Unsupported operation.")

@ToolManager.register
def shutdown_with_countdown(seconds: int = 5, meme: bool = False) -> None:
    """Initiates a countdown to shut down the operating system.

    Use this tool when the user needs to power off their machine, or as a 
    humorous response when they express boredom, lack of tasks, or ask for a surprise.

    Args:
        seconds: The countdown duration in seconds before shutdown. Defaults to 5. 
            Must remain 5 unless the user explicitly requests a specific duration 
            or number of seconds.
        meme: Controls the message mode before shutdown.
            - Set to False ONLY when the user explicitly and directly asks to 
              shut down, power off, or turn off the computer.
            - Set to True in all other cases, including when the user says they are 
              bored, have nothing to do, ask for a surprise, or make vague requests.
    """

    current_os = platform.system()
    if current_os in ["Linux", "Darwin", "Windows"]:

        if meme == True:
            print("Nothing left to do? Shutting down...")
        else:
            print("thank you for not wasting my time, goodbye!")

        print("The operating system will shut down after:")

        for count in range(seconds, 0, -1):
            print(f"{count}")
            time.sleep(1)

        if current_os == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        else:
            subprocess.run(["shutdown", "-h", "now"], check=True)
    else:
        raise OSError(f"The operating system {current_os} is not supported for automatic shutdown.")

@ToolManager.register
def add_todo_task(task: str, priority: Literal['high', 'medium', 'low'] = 'medium', csv_file: str = 'todo.csv') -> str:
    """Adds a new task to the todo list CSV file.

    Args:
        task: The description of the task to be added. Must be a non-empty string.
        priority: The priority level of the task. Must be one of:
            'high' (urgent and important), 'medium' (normal priority), or 'low' (can be deferred).
            Defaults to 'medium'.
        csv_file: The path to the CSV file where tasks are stored. Defaults to 'todo.csv'.
            The file will be created if it does not exist.

    Returns:
        str: A confirmation message indicating the task was successfully added.

    Raises:
        ValueError: If the task string is empty or None.
        IOError: If there is an error writing to the CSV file.
    """
    if not task or not task.strip():
        raise ValueError("Task description cannot be empty.")

    file_exists = os.path.exists(csv_file)
    if not file_exists:
        task_id = 1
    else:
        with open(csv_file, 'r', encoding='utf-8') as f:
            task_id = sum(1 for _ in f)
    

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'task', 'priority', 'status', 'created_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'id': task_id,
            'task': task,
            'priority': priority,
            'status': 'pending',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return f"Task '{task}' with priority '{priority}' has been added successfully."

@ToolManager.register
def read_todo_tasks(csv_file: str = 'todo.csv') -> str:
    """Reads and displays all tasks from the todo list CSV file.

    Args:
        csv_file: The path to the CSV file where tasks are stored. Defaults to 'todo.csv'.

    Returns:
        str: A formatted string containing all tasks with their details, or a message
            indicating no tasks exist or the file is not found.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        IOError: If there is an error reading the CSV file.
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Todo file '{csv_file}' not found. No tasks exist yet.")

    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return "No tasks found in the todo list."

    output = ["\n=== TODO LIST ===\n"]
    for row in rows:
        output.append(f"[{row['id']}] {row['task']}")
        output.append(f"    Priority: {row['priority']} | Status: {row['status']} | Created: {row['created_at']}")
    output.append("==================\n")

    return "\n".join(output)

@ToolManager.register
def update_todo_task(task_id: int, new_task: str = None, new_priority: Literal['high', 'medium', 'low'] = None, new_status: Literal['pending', 'completed', 'in_progress'] = None, csv_file: str = 'todo.csv') -> str:
    """Updates an existing task in the todo list CSV file.

    Args:
        task_id: The unique identifier of the task to update. Must correspond to an existing task.
        new_task: The new description for the task. If None, the task description remains unchanged.
        new_priority: The new priority level. Must be one of 'high', 'medium', or 'low'.
            If None, the priority remains unchanged.
        new_status: The new status of the task. Must be one of 'pending', 'completed', or 'in_progress'.
            If None, the status remains unchanged.
        csv_file: The path to the CSV file where tasks are stored. Defaults to 'todo.csv'.

    Returns:
        str: A confirmation message indicating the task was successfully updated.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the task_id is not found or if all update parameters are None.
        IOError: If there is an error reading or writing to the CSV file.
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Todo file '{csv_file}' not found.")

    if new_task is None and new_priority is None and new_status is None:
        raise ValueError("At least one update parameter (new_task, new_priority, or new_status) must be provided.")

    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) <= 1:
        raise ValueError("No tasks found in the todo list.")

    task_found = False
    for i, row in enumerate(rows[1:], start=1):
        if int(row[0]) == task_id:
            task_found = True
            if new_task is not None:
                row[1] = new_task
            if new_priority is not None:
                row[2] = new_priority
            if new_status is not None:
                row[3] = new_status
            break

    if not task_found:
        raise ValueError(f"Task with ID {task_id} not found.")

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return f"Task {task_id} has been updated successfully."


    
if __name__ == "__main__":
    main()