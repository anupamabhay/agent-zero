from langchain_core.tools import tool
from datetime import datetime, timedelta
from dateutil import parser
from typing import List, Dict


@tool
def create_routine(
    tasks_with_deadlines: List[Dict[str, str]],
    working_hours_start: str = "09:00",
    working_hours_end: str = "17:00",
) -> str:
    """Generates a realistic daily routine based on a list of tasks and their deadlines.
    tasks_with_deadlines format: [{"task": "Study Math", "deadline": "2026-02-05", "priority": "high", "estimated_hours": "2"}]
    """
    try:
        # Simple heuristic-based scheduling
        now = datetime.now()
        start_time = parser.parse(working_hours_start).time()
        end_time = parser.parse(working_hours_end).time()

        # Sort tasks by deadline
        sorted_tasks = sorted(
            tasks_with_deadlines, key=lambda x: parser.parse(x["deadline"])
        )

        routine = [f"### Generated Routine (Starting {now.strftime('%Y-%m-%d')})"]
        current_day = now

        for task in sorted_tasks:
            deadline = parser.parse(task["deadline"])
            hours = float(task.get("estimated_hours", 1))

            routine.append(
                f"- **{task['task']}** (Deadline: {deadline.strftime('%Y-%m-%d')})"
            )
            routine.append(
                f"  Allocated: {hours} hours | Priority: {task.get('priority', 'medium')}"
            )

        routine.append(
            "\n*Note: This is a high-level allocation. Please breaks tasks into chunks if they exceed 4 hours.*"
        )

        return "\n".join(routine)
    except Exception as e:
        return f"Error creating routine: {str(e)}"
