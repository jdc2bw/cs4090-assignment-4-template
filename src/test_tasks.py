import pytest
import tempfile
import os
import json
from tasks import *
from datetime import datetime, timedelta

@pytest.fixture
def sample_tasks():
    return [
        {
            "id": 1,
            "title": "Task One",
            "description": "First task",
            "priority": "High",
            "category": "Work",
            "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 2,
            "title": "Task Two",
            "description": "Second task",
            "priority": "Low",
            "category": "Personal",
            "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]

def test_save_and_load_tasks(sample_tasks):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        save_tasks(sample_tasks, file_path=tf.name)
        loaded = load_tasks(file_path=tf.name)
        assert loaded == sample_tasks
    os.unlink(tf.name)

def test_generate_unique_id(sample_tasks):
    new_id = generate_unique_id(sample_tasks)
    assert new_id == 3

def test_filter_tasks_by_priority(sample_tasks):
    high_priority = filter_tasks_by_priority(sample_tasks, "High")
    assert len(high_priority) == 1
    assert high_priority[0]["title"] == "Task One"

def test_filter_tasks_by_category(sample_tasks):
    personal_tasks = filter_tasks_by_category(sample_tasks, "Personal")
    assert len(personal_tasks) == 1
    assert personal_tasks[0]["title"] == "Task Two"

def test_filter_tasks_by_completion(sample_tasks):
    # Mark one as completed
    sample_tasks[0]["completed"] = True
    completed = filter_tasks_by_completion(sample_tasks, completed=True)
    incomplete = filter_tasks_by_completion(sample_tasks, completed=False)
    assert len(completed) == 1
    assert completed[0]["title"] == "Task One"
    assert len(incomplete) == 1
    assert incomplete[0]["title"] == "Task Two"

def test_search_tasks(sample_tasks):
    results = search_tasks(sample_tasks, "first")
    assert len(results) == 1
    assert results[0]["title"] == "Task One"

def test_get_overdue_tasks(sample_tasks):
    overdue = get_overdue_tasks(sample_tasks)
    assert len(overdue) == 1
    assert overdue[0]["title"] == "Task Two"

def test_load_tasks_file_not_found():
    # Load from a non-existing file
    non_existing_file = "non_existing_tasks.json"
    tasks = load_tasks(file_path=non_existing_file)
    assert tasks == []

def test_load_tasks_invalid_json(tmp_path):
    # Create invalid JSON file
    bad_file = tmp_path / "bad_tasks.json"
    bad_file.write_text("{ invalid json }")
    tasks = load_tasks(file_path=str(bad_file))
    assert tasks == []

def test_generate_unique_id_empty_list():
    tasks = []
    new_id = generate_unique_id(tasks)
    assert new_id == 1

def test_filter_tasks_by_priority_no_match(sample_tasks):
    none_priority = filter_tasks_by_priority(sample_tasks, "Urgent")
    assert none_priority == []

def test_filter_tasks_by_category_no_match(sample_tasks):
    none_category = filter_tasks_by_category(sample_tasks, "Fitness")
    assert none_category == []

def test_search_tasks_no_match(sample_tasks):
    results = search_tasks(sample_tasks, "nonexistent")
    assert results == []

def test_get_overdue_tasks_no_overdue(sample_tasks):
    # Make all tasks not overdue
    for task in sample_tasks:
        task["due_date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    overdue = get_overdue_tasks(sample_tasks)
    assert overdue == []

# tests for new feature no. 1 (task search)

def test_search_tasks_title(sample_tasks):
    results = search_tasks(sample_tasks, "Task One")
    assert len(results) == 1
    assert results[0]["id"] == 1

def test_search_tasks_description(sample_tasks):
    results = search_tasks(sample_tasks, "First task")
    assert len(results) == 1
    assert results[0]["id"] == 1

def test_search_tasks_case_insensitive(sample_tasks):
    results = search_tasks(sample_tasks, "task one")  # lower case
    assert len(results) == 1
    assert results[0]["id"] == 1

def test_search_tasks_no_match(sample_tasks):
    results = search_tasks(sample_tasks, "Nonexistent")
    assert results == []

# tests for new feature no. 2 (tasks due soon)

def test_get_due_soon_tasks(sample_tasks):
    # Adjust sample_tasks so one is due within 24h
    sample_tasks[0]["due_date"] = (datetime.now() + timedelta(hours=23)).strftime("%Y-%m-%d")
    sample_tasks[1]["due_date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    due_soon = get_due_soon_tasks(sample_tasks)
    
    assert len(due_soon) == 1
    assert due_soon[0]["title"] == "Task One"

def test_get_due_soon_tasks_none(sample_tasks):
    # Make all tasks far in the future
    for task in sample_tasks:
        task["due_date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    due_soon = get_due_soon_tasks(sample_tasks)
    
    assert due_soon == []

def test_sort_tasks_by_priority(sample_tasks):
    # Swap priorities for testing
    sample_tasks[0]["priority"] = "Low"
    sample_tasks[1]["priority"] = "High"
    
    sorted_tasks = sort_tasks_by_priority(sample_tasks)
    
    assert sorted_tasks[0]["priority"] == "High"
    assert sorted_tasks[1]["priority"] == "Low"

def test_sort_tasks_by_due_date(sample_tasks):
    # Set due dates for testing
    sample_tasks[0]["due_date"] = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    sample_tasks[1]["due_date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    sorted_tasks = sort_tasks_by_due_date(sample_tasks)
    
    assert sorted_tasks[0]["due_date"] < sorted_tasks[1]["due_date"]

