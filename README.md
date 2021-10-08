# karen-bot

A helpful Discord/Slack bot for CDT-managed servers.

## Installation

```bash
# Python >=3.9, <3.11
poetry install
poetry shell
python main.py
```

## Configuration

Create a file named `config.toml` in the same directory and follow the template:

```toml
# Discord Token
token = ""
# Channel ID for anonymous questions
question_id = ""
# Role ID for Officers
officer_role_id = ""
# Command prefix
prefix = "!"
```

## License

All code in this repository is licensed under the GNU GPL v3, see [LICENSE](https://github.com/sdsucdt/karen-bot/blob/master/LICENSE) for more information.
