import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.agent.agent import HealthAgent
from core.orchestrator.core import OrchestrateAgent
from tools.fitness_recommender import FitnessRecommender
from tools.guidelines import GuidelinesVerifier

SHOW_THINKING = "--thinking" in sys.argv

def boot():
    """Eager boot-time initialisation — runs before the first user query."""
    print("Initialising…")
    FitnessRecommender.load_or_train()   # train if needed, cache to disk + singleton
    verifier = GuidelinesVerifier.load()
    orchestrator = OrchestrateAgent(HealthAgent("HealthCoach"), verifier=verifier)
    print("Ready.\n")
    return orchestrator 

def main():
    print("Health Coach — type 'quit' to exit\n")
    orchestrator = boot()

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

        print("\nCoach: ")
        result = orchestrator.run(user_input)

        if SHOW_THINKING and result.get("thinking"):
            print(f"\n--- Thinking ---\n{result['thinking']}\n--- End ---\n")


if __name__ == "__main__":
    main()
