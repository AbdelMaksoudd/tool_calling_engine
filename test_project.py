import pytest
import os
import csv
import tempfile
from project import calculator, add_todo_task, read_todo_tasks


def test_calculator():
    assert calculator('+', 5, 3) == 8
    assert calculator('-', 10, 4) == 6
    assert calculator('*', 7, 2) == 14
    assert calculator('/', 20, 4) == 5
    assert calculator('+', 2.5, 3.5) == 6.0

    with pytest.raises(ZeroDivisionError):
        calculator('/', 10, 0)

    with pytest.raises(ValueError):
        calculator('%', 10, 5)


def test_add_todo_task(tmp_path):
    csv_file = tmp_path / "test_todo.csv"

    result = add_todo_task("Test task", "high", str(csv_file))
    assert "successfully added" in result.lower()

    assert os.path.exists(csv_file)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['id', 'task', 'priority', 'status', 'created_at']
        row = next(reader)
        assert row['priority'] == 'high'

    with pytest.raises(ValueError, match="cannot be empty"):
        add_todo_task("", csv_file=str(csv_file))

    with pytest.raises(ValueError, match="cannot be empty"):
        add_todo_task("   ", csv_file=str(csv_file))


def test_read_todo_tasks(tmp_path):
    csv_file = tmp_path / "test_todo.csv"

    add_todo_task("Task 1", "high", str(csv_file))
    add_todo_task("Task 2", "low", str(csv_file))
    result = read_todo_tasks(str(csv_file))
    assert "Task 1" in result
    assert "Task 2" in result
    assert "TODO LIST" in result

    csv_file_not_found = tmp_path / "nonexistent.csv"
    with pytest.raises(FileNotFoundError, match="not found"):
        read_todo_tasks(str(csv_file_not_found))

    csv_file_empty = tmp_path / "empty.csv"
    with open(csv_file_empty, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'task', 'priority', 'status', 'created_at'])
        writer.writeheader()
    result = read_todo_tasks(str(csv_file_empty))
    assert "No tasks found" in result
