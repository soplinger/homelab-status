import unittest

from server import is_allowed_host, parse_port
from status import collect_status, parse_meminfo, parse_uptime


class TestParsers(unittest.TestCase):
    def test_parse_meminfo_reads_total_and_available_in_bytes(self):
        text = "MemTotal:       6000000 kB\nMemFree:        100000 kB\nMemAvailable:   4000000 kB\n"
        self.assertEqual(
            parse_meminfo(text),
            {"total": 6000000 * 1024, "available": 4000000 * 1024},
        )

    def test_parse_meminfo_falls_back_to_memfree_without_memavailable(self):
        text = "MemTotal:       6000000 kB\nMemFree:        100000 kB\n"
        self.assertEqual(parse_meminfo(text)["available"], 100000 * 1024)

    def test_parse_meminfo_without_memtotal_raises_value_error(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemFree:        100000 kB\n")

    def test_parse_uptime_reads_first_field(self):
        self.assertEqual(parse_uptime("4441.25 15000.10\n"), 4441.25)


class TestServerHelpers(unittest.TestCase):
    def test_host_check_allows_only_local_names_on_the_port(self):
        self.assertTrue(is_allowed_host("127.0.0.1:8080", 8080))
        self.assertTrue(is_allowed_host("localhost:8080", 8080))

    def test_host_check_rejects_other_hosts_and_ports(self):
        self.assertFalse(is_allowed_host("evil.example:8080", 8080))
        self.assertFalse(is_allowed_host("127.0.0.1:9999", 8080))
        self.assertFalse(is_allowed_host("", 8080))

    def test_parse_port_defaults_and_rejects_bad_input(self):
        self.assertEqual(parse_port(["server.py"]), 8080)
        self.assertEqual(parse_port(["server.py", "9000"]), 9000)
        with self.assertRaises(SystemExit):
            parse_port(["server.py", "eighty"])
        with self.assertRaises(SystemExit):
            parse_port(["server.py", "70000"])


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
