# secure-journal

CLI tool for encrypted journaling

Requires emacs to be installed.
Requires Ollama with deepseek-r1 to be running locally.

## Installation

```bash
git clone https://github.com/charliemarlow/secure-journal.git
cd secure-journal
pip install .
```

### Deepseek-r1

Download ollama here: https://ollama.com/download

and then run:

```bash
ollama run deepseek-r1
```

## Usage

```bash
secure-journal my_journal
```

You'll be guided to create a password and then you can start writing your journal entries.
After creating a journal entry, it will be encrypted & saved. You can view your journal entries by running the command again.

```bash
secure-journal my_journal --read filename
```

Your journal entries will automatically be sent to a local LLM for analysis. You can retry the analysis using the `--therapy` flag.

```bash
secure-journal my_journal --therapy filename
```
