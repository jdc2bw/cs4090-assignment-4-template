import subprocess
import re
import streamlit as st
import pandas as pd
from datetime import datetime
from tasks import *

def main():
    st.title("To-Do Application")
    
    # Load existing tasks
    tasks = load_tasks()

    # Sidebar for adding new tasks
    st.sidebar.header("Add New Task")
    
    # Task creation form
    with st.sidebar.form("new_task_form"):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date = st.date_input("Due Date")
        submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title and task_description and datetime.now().date() <= task_due_date:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d H:%M:%S")
            }
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")

    if "developer_mode" not in st.session_state:
        st.session_state["developer_mode"] = False

    # Sidebar for Developer Tools
    st.sidebar.header("Settings")

    # Developer Mode toggle
    developer_mode = st.sidebar.checkbox("Developer Mode", value=st.session_state["developer_mode"])
    st.session_state["developer_mode"] = developer_mode

    if developer_mode:
        # developer tools
        st.sidebar.header("Developer Tools")

        if st.sidebar.button("Run Unit Tests"):
            with st.spinner("Running unit tests..."):
                result = subprocess.run(
                    ["pytest", "--maxfail=1", "--disable-warnings", "-q"], 
                    capture_output=True, text=True
                )
        
            test_passed = result.returncode == 0
            output = result.stdout
        
            if test_passed:
                st.sidebar.success("All tests passed!")
            else:
                st.sidebar.error("Tests failed.")
        
            with st.expander("Test Output (Unit Tests)"):
                st.code(output)
    
        if st.sidebar.button("Show Code Coverage"):
            with st.spinner("Computing code coverage..."):
                result = subprocess.run(
                    ["pytest", "--cov=tasks", "--cov-report=term-missing", "--maxfail=1", "--disable-warnings", "-q"], 
                    capture_output=True, text=True
                )
    
            output = result.stdout
    
            coverage_match = re.search(r"TOTAL.*?(\d+)%", output)
            if coverage_match:
                coverage_percent = int(coverage_match.group(1))
                st.sidebar.metric(label="Code Coverage", value=f"{coverage_percent}%")
                st.sidebar.progress(coverage_percent / 100)
            else:
                st.sidebar.warning("Could not determine code coverage.")
        
            with st.expander("Test Output (Coverage Report)"):
                st.code(output)
    
        if st.sidebar.button("Generate HTML Coverage Report"):
            with st.spinner("Generating HTML coverage report..."):
                result = subprocess.run(
                    ["pytest", "--cov=tasks", "--cov-report=html", "--maxfail=1", "--disable-warnings", "-q"],
                    capture_output=True, text=True
                )
    
            output = result.stdout
    
            if result.returncode == 0:
                st.sidebar.success("HTML coverage report generated.")
            else:
                st.sidebar.error("Tests failed while generating report")
        
            with st.expander("Test Output (HTML Report)"):
                st.code(output)
        
            st.sidebar.info("Open the file: `htmlcov/index.html` to view the coverage report.")


    # Main area to display tasks
    st.header("Your Tasks")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in tasks])))
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    show_completed = st.checkbox("Show Completed Tasks")
    
    # Apply filters
    filtered_tasks = tasks.copy()
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task["completed"]]

    # for new feature no. 1, searching tasks.
    search_query = st.text_input("Search Tasks", "")

    # Apply search if query is entered
    filtered_tasks = tasks.copy()
    
    if search_query:
        filtered_tasks = search_tasks(filtered_tasks, search_query)
    
    # Then apply filters (category, priority, etc.)
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task["completed"]]
        
    due_soon_tasks = get_due_soon_tasks(tasks)

    if due_soon_tasks:
        with st.expander("Tasks Due Soon (Next 24h)"):
            for task in due_soon_tasks:
                st.warning(f"**{task['title']}** due on {task['due_date']}")
                
    sort_option = st.selectbox("Sort Tasks By", ["None", "Priority", "Due Date"])
    if sort_option == "Priority":
        filtered_tasks = sort_tasks_by_priority(filtered_tasks)
    elif sort_option == "Due Date":
        filtered_tasks = sort_tasks_by_due_date(filtered_tasks)

    # Display tasks
    for task in filtered_tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            if task["completed"]:
                st.markdown(f"~~**{task['title']}**~~")
            else:
                st.markdown(f"**{task['title']}**")
            st.write(task["description"])
            st.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
        with col2:
            if st.button("Complete" if not task["completed"] else "Undo", key=f"complete_{task['id']}"):
                for t in tasks:
                    if t["id"] == task["id"]:
                        t["completed"] = not t["completed"]
                        save_tasks(tasks)
                        st.rerun()
            if st.button("Delete", key=f"delete_{task['id']}"):
                tasks = [t for t in tasks if t["id"] != task["id"]]
                save_tasks(tasks)
                st.rerun()

if __name__ == "__main__":
    main()
