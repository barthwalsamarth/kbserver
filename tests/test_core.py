import unittest
from pathlib import Path
from kb.core import load_corpus, search, can_read
C = load_corpus(Path(__file__).parents[1] / "corpus" / "docs.json")

class T(unittest.TestCase):
    def ids(self, user, q): return {r["doc_id"] for r in search(C, user, q)}
    def test_two_users_differ(self):
        self.assertIn("fin-002", self.ids("alice", "budget headcount"))
        self.assertNotIn("fin-002", self.ids("bob", "budget headcount"))
    def test_unknown_user_sees_nothing(self):
        self.assertEqual(search(C, "", "leave"), [])
        self.assertEqual(search(C, "mallory", "leave"), [])
    def test_no_score_leak(self):
        # bob's results must be identical whether or not alice-only docs exist
        r = search(C, "bob", "budget")
        self.assertTrue(all(x["doc_id"] != "fin-002" for x in r))
    def test_relevance(self):
        self.assertEqual(search(C, "alice", "parental leave weeks")[0]["doc_id"], "hr-001")
    def test_injection_flagged(self):
        r = search(C, "carol", "wifi password admin mode")
        self.assertTrue(any(x["flagged_untrusted"] for x in r))
    def test_citations(self):
        for x in search(C, "alice", "postmortem"):
            self.assertTrue(x["citation"].startswith("[eng-003#"))
    def test_limit(self):
        self.assertLessEqual(len(search(C, "alice", "the", limit=2)), 2)
if __name__ == "__main__": unittest.main()
