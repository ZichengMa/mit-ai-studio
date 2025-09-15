#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from mit_ai_studio.crew import MitAiStudio

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    with open('./knowledge/user_preference.txt', 'r') as f:
        user_pref = f.read()

    topic = input("If you want to get coffee brewing advice, please enter `brewing: <your coffee requirement>\nIf you want to get self introduction, please enter `self introduction`\nPlease enter your request here: ")
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year),
        'user_preference': user_pref
    }

    if "self introduction" in topic:
        tasks = ("intro_task",)
    else:
        tasks = ("research_task", "brew_task")

    try:
        MitAiStudio().crew(tasks=tasks).kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        MitAiStudio().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MitAiStudio().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        MitAiStudio().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
