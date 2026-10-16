import unittest
from kb.auth import parse_tokens, lookup

class T(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_tokens("a:alice, b:bob"), {"a": "alice", "b": "bob"})
        self.assertEqual(parse_tokens(""), {})
        self.assertEqual(parse_tokens("novalue,:x,y:"), {})
    def test_lookup(self):
        t = {"tok-a": "alice", "tok-b": "bob"}
        self.assertEqual(lookup(t, "tok-a"), "alice")
        self.assertEqual(lookup(t, "tok-b"), "bob")
    def test_reject(self):
        t = {"tok-a": "alice"}
        for bad in ("", None, "tok-A", "tok-a ", "tok"):
            self.assertIsNone(lookup(t, bad))
if __name__ == "__main__": unittest.main()
