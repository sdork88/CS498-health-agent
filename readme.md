# FitAgent — A Specialized Health & Fitness Agent

## Overview

FitAgent is a domain-specific AI health coaching agent designed to outperform generic LLMs on safety-critical fitness and nutrition tasks. Built for users who need unified, personalized guidance spanning workout planning, nutrition, goal tracking, and medical condition awareness, FitAgent combines structured tool use, traceable reasoning, and meaningful safety guardrails to deliver more reliable, evidence-based recommendations than general-purpose models.

This project was developed as part of CS 498 (Spring 2026) and includes both the agent implementation and a reproducible benchmark for evaluating health and fitness AI agents — the first of its kind targeting multi-turn planning, personalization, and safety compliance in this domain.

---

## 🧠 Core Features

- Personalized health and fitness recommendations grounded in ACSM, HHS, WHO, and USDA standards
- Persistent memory for user goals, medical conditions, allergies, and progress via the Health Memory Tool
- Integration with a KNN fitness recommender, nutrition tools, and domain-scoped web search
- Adaptive multi-turn coaching with context retention across conversation turns
- Safety guardrails enforced by a GuidelinesVerifier that cross-checks responses against HHS Physical Activity Guidelines
- Extended thinking via Claude Sonnet 4.5 for deep, evidence-based reasoning

---

## 🏗️ Project Structure

```
CS_498_AGENTS/
│
├── CS498-health-agent/
│   └── src/
│       ├── core/
│       │   ├── agent.py        # Main agent logic and orchestration
│       │   ├── core.py         # Core agent loop and reasoning logic
│       │   └── models.py       # Agent and memory data models
│       │
│       └── tools/
│           └── models.py       # Tool interfaces (e.g., calorie calc, workout planner)
│
└── requirements.txt            # Python dependencies
```

---

## 🧩 Components

| Module | Description |
|---|---|
| `agent.py` | Orchestrates the full request lifecycle — builds user context, runs the agent loop, initializes infrastructure, and enforces safety checks before responses reach the user |
| `core.py` | Core reasoning, message handling, and context management; drives multi-turn conversation with Claude Sonnet 4.5 (extended thinking, 16,000 max output tokens, 3,000-token thinking budget) |
| `models.py` | Defines user profiles (name, age, weight, height, sex, fitness goal, medical conditions, allergies), health metrics, and agent state via the in-memory `HealthUser` object |
| `tools/models.py` | Exposes the tool layer: Health Memory Tool (get/set/get_all across 8 profile fields), KNN Fitness Recommender (returns 5 nearest-neighbor workout and diet plans), and Scoped Web Search restricted to trusted health sources (nih.gov, cdc.gov, mayoclinic.org, healthline.com, webmd.com) |

---

## 🏛️ Agent Architecture

FitAgent uses a 4-layer architecture:

1. **Orchestration Layer** — Drives the request lifecycle, builds context, runs the agent loop, initializes infrastructure, and enforces safety checks before any response reaches the user.
2. **Agent Layer** — Claude Sonnet 4.5 with extended thinking. A large token budget is allocated for deep reasoning.
3. **Tool Layer** — Health Memory Tool | KNN Fitness Recommender | Nutrition tools | Domain-scoped web search | GuidelinesVerifier (safety)
4. **State Layer** — User profile | Conversation history | Trained KNN model | HHS Physical Activity Guidelines PDF

The **dynamic system prompt** expands as user profile fields populate via `context_for()`, ensuring the model always has full user health context when generating responses.

The **GuidelinesVerifier** performs keyword searches against the HHS Physical Activity Guidelines PDF and issues corrections when conflicts with the user profile or response text are identified. It uses a `GUIDELINES_OK` sentinel to skip verification when no relevant sections are found.

---

## 🧪 Evaluation

### Benchmark Design

FitAgent is evaluated against a custom 20-task benchmark spanning 4 capability domains and 3 difficulty tiers:

| Domain | Coverage |
|---|---|
| Workout Planning | Exercise prescription, injury-modified plans |
| Meal & Nutrition Guidance | Macronutrient targets, allergy-aware planning |
| Goal Setting & Progress Tracking | Multi-turn progress evaluation |
| Health Condition Recommendations | Medical constraint handling |

| Difficulty | # Tasks | Behaviors/Task | Max Points | Complexity |
|---|---|---|---|---|
| Easy | 7 | 3 | 21 | Single-step, single-domain retrieval |
| Medium | 7 | 4 | 28 | Multi-step or multi-constraint tasks |
| Hard | 6 | 5 | 30 | Multi-domain, multi-turn tasks |
| **Total** | **20** | — | **79 pts** | |

### Scoring Methods

Each task is run 3× per agent and scored using three complementary methods:

- **Cosine Similarity** — Embedding similarity vs. ideal response; threshold ≥ 0.75 to pass
- **LLM-as-Judge** — Claude evaluates each response against behavior descriptions and returns a binary pass/fail
- **Human-in-the-Loop** — Binary grading with ≥85% grader agreement required; graders are blinded to which agent produced each response

Safety behaviors use the **minimum score** across all trials (worst-case retained). All other behaviors use the average.

### Validation

Rubrics are grounded in ACSM, HHS, WHO, and USDA FoodData Central standards. Exercise prescription is validated via a KNN model and the HHS Physical Activity Guidelines PDF accessed via MCP tool use.

### Key Metrics

| Metric | Target | Description |
|---|---|---|
| Total Benchmark Score | ≥63 / 79 good | Sum of all behavior scores |
| Task Pass Rate | ≥80% | Fraction of tasks where all behaviors pass |
| Context Utilization Score | ≥90% | Multi-turn tasks where agent correctly uses prior context |
| Safety Compliance Rate | 100% required | Safety behaviors retain the lowest trial score |
| Human Helpfulness Rating | ≥7 / 10 | Collected from blinded graders |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| AI Model | Anthropic Claude Sonnet 4.5 (extended thinking) |
| ML | scikit-learn KNN |
| Safety | HHS Physical Activity Guidelines PDF + GuidelinesVerifier |
| Web Search | Anthropic web search tool (domain-scoped) |
| Data Sources | ACSM, HHS, WHO, USDA FoodData Central |

---

## 👥 Contributors

Anoop Bhaskar, Jon Temkin, Spencer Dork — Group 5 | CS 498 | Spring 2026
