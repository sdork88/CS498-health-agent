import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.agent.agent import HealthAgent
from core.orchestrator.core import OrchestrateAgent
from tools.fitness_recommender import FitnessRecommender
from tools.guidelines import GuidelinesVerifier

SHOW_THINKING = "--thinking" in sys.argv


def main():
    print("Health Coach — type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye! Keep up with your health goals!")
            break

        print("\nCoach: ", end="", flush=True)
        result = orchestrator.run(user_input)

        if SHOW_THINKING and result.get("thinking"):
            print(f"\n--- Thinking ---\n{result['thinking']}\n--- End ---\n")
        else:
            print()


if __name__ == "__main__":
    main()
