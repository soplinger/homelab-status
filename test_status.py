import unittest

from status import collect_status, parse_meminfo, parse_uptime


class TestParsers(unittest.TestCase):
    def test_parse_meminfo_reads_total_and_available_in_bytes(self):
        text = "MemTotal:       6000000 kB\nMemFree:        100000 kB\nMemAvailable:   4000000 kB\n"
        self.assertEqual(
            parse_meminfo(text),
            {"total": 6000000 * 1024, "available": 4000000 * 1024},
        )

    def test_parse_uptime_reads_first_field(self):
        self.assertEqual(parse_uptime("4441.25 15000.10\n"), 4441.25)


class TestCollectStatus(unittest.TestCase):
    def test_collect_status_has_expected_shape(self):
        status = collect_status()
        self.assertEqual(
            set(status),
            {"hostname", "uptime_seconds", "load", "memory", "disk", "tmux_sessions"},
        )
        self.assertGreater(status["memory"]["total"], 0)
        self.assertGreater(status["disk"]["total"], 0)
        self.assertIsInstance(status["tmux_sessions"], list)


if __name__ == "__main__":
    unittest.main()
