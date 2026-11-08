import unittest

from src.prompts.adjudicator import AdjudicatorPrompts


class AdjudicatorPromptTests(unittest.TestCase):
    def test_prompt_includes_context_and_limits(self):
        prompt = AdjudicatorPrompts.get_adjudicator_prompt("Question?", "Answer.", "accuracy issue", "conflict")
        for part in ("Question?", "Answer.", "accuracy issue", "conflict"):
            self.assertIn(part, prompt)
        system = AdjudicatorPrompts.ADJUDICATOR_SYSTEM_PROMPT
        for part in ("uncertainty", "Do not invent", "independent", "reason"):
            self.assertIn(part, system)
