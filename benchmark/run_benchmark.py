import sys
import os
import json
import argparse
import io
import contextlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from core.agent.agent import HealthAgent
from core.orchestrator.core import OrchestrateAgent
from tools.fitness_recommender import FitnessRecommender
from tools.guidelines import GuidelinesVerifier


def load_tasks(tasks_dir: Path, task_ids: list[str] | None = None) -> list[dict]:
    tasks = []
    for path in sorted(tasks_dir.glob("task*.json")):
        task = json.loads(path.read_text())
        if task_ids and task["task_id"] not in task_ids:
            continue
        tasks.append(task)
    return tasks


def build_orchestrator() -> OrchestrateAgent:
    """Fresh orchestrator (and fresh agent) per task to avoid state bleed."""
    verifier = GuidelinesVerifier.load()
    return OrchestrateAgent(HealthAgent("HealthCoach"), verifier=verifier)


def run_task(task: dict) -> dict:
    orchestrator = build_orchestrator()
    buf = io.StringIO()

    turns = task.get("turns", [])
    last_result = None

    with contextlib.redirect_stdout(buf):
        for turn in turns:
            if turn.get("role") == "user":
                last_result = orchestrator.run(turn["message"])

    return {
        "task_id": task["task_id"],
        "difficulty": task.get("difficulty"),
        "task_category": task.get("task_category"),
        "primary_capability": task.get("primary_capability"),
        "turns": turns,
        "agent_response": last_result["response"] if last_result else "",
        "status": "ok",
    }


def main():
    parser = argparse.ArgumentParser(description="Run FitAgent benchmark tasks")
    parser.add_argument("--tasks", help="Comma-separated task IDs to run (e.g. T01,T03)")
    parser.add_argument("--out", help="Output file path (default: benchmark/results/run_<timestamp>.json)")
    args = parser.parse_args()

    task_ids = [t.strip() for t in args.tasks.split(",")] if args.tasks else None

    tasks_dir = Path(__file__).parent / "tasks"
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    out_path = Path(args.out) if args.out else results_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    tasks = load_tasks(tasks_dir, task_ids)
    if not tasks:
        print("No tasks found.")
        sys.exit(1)

    print(f"Initialising agent…")
    FitnessRecommender.load_or_train()
    print(f"Running {len(tasks)} task(s)…\n")

    run_timestamp = datetime.now().isoformat()
    results = []
    for i, task in enumerate(tasks, 1):
        tid = task["task_id"]
        print(f"[{i}/{len(tasks)}] {tid}: {task.get('primary_capability', '')} … ", end="", flush=True)
        try:
            result = run_task(task)
            print("done")
        except Exception as exc:
            result = {"task_id": tid, "status": "error", "error": str(exc)}
            print(f"ERROR: {exc}")
        results.append(result)

        # Write after every task so partial runs are recoverable
        output = {
            "run_timestamp": run_timestamp,
            "total_tasks": len(results),
            "results": results,
        }
        out_path.write_text(json.dumps(output, indent=2))

    print(f"\nResults saved to {out_path}")
    print(f"Grade with: python benchmark/judge.py --results {out_path}")


if __name__ == "__main__":
    main()
