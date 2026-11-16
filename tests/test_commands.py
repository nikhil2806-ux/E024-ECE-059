import tempfile
import unittest
from pathlib import Path

from main import execute_commands
from src.loader import InputDataError

PROJECT = Path(__file__).resolve().parents[1]


class CommandInterpreterTests(unittest.TestCase):
    def test_commands_execute_in_file_order_and_create_both_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out"
            count_requests, count_quotes = execute_commands(PROJECT / "commands.txt", output)
            self.assertEqual((count_requests, count_quotes), (30, 30))
            self.assertTrue((output / "quotations.csv").exists())
            self.assertTrue((output / "fleet_usage.csv").exists())

    def test_quote_all_before_loading_inputs_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            commands = Path(temp) / "commands.txt"
            commands.write_text("QUOTE_ALL\n", encoding="utf-8")
            with self.assertRaisesRegex(InputDataError, "load rate card and requests"):
                execute_commands(commands, Path(temp) / "out")

    def test_unknown_command_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            commands = Path(temp) / "commands.txt"
            commands.write_text("DO_MAGIC\n", encoding="utf-8")
            with self.assertRaisesRegex(InputDataError, "unknown command"):
                execute_commands(commands, Path(temp) / "out")

    def test_missing_print_command_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            commands = Path(temp) / "commands.txt"
            commands.write_text(
                f"LOAD_RATE_CARD|{PROJECT / 'rate_card.csv'}\n"
                f"LOAD_REQUESTS|{PROJECT / 'requests.csv'}\n"
                "QUOTE_ALL\nPRINT_QUOTES\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(InputDataError, "PRINT_FLEET"):
                execute_commands(commands, Path(temp) / "out")


if __name__ == "__main__":
    unittest.main()
