# Start here on your Mac

You do not need to know Python to run the first demonstration. Follow these steps in order.

## 1. Check Python

1. Open **Terminal** (press Command + Space, type `Terminal`, press Enter).
2. Copy this command and press Enter:

   ```bash
   python3 --version
   ```

3. You need Python 3.10 or newer. If Terminal says the command was not found, install Python 3 from the official macOS download at https://www.python.org/downloads/macos/ and then reopen Terminal.

## 2. Open the project folder

1. Download and extract `permission-delta-starter.zip`.
2. In Terminal, type `cd ` (include a space after `cd`).
3. Drag the extracted `permission-delta` folder from Finder into the Terminal window. Terminal will fill in its path.
4. Press Enter.

## 3. Run the tests

Copy and run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

You should see all tests finish with `OK`.

## 4. Run the sample scan

Copy and run:

```bash
PYTHONPATH=src python3 -m permission_delta compare examples/before.json examples/after.json
```

You should see a Markdown report that identifies a shell executable, a new remote MCP server, and changed environment variable configuration. It must not show the example secret values, URL path, or URL query token.

## 5. Open the code in VS Code

If Visual Studio Code is installed, run this from the project folder:

```bash
code .
```

If the `code` command is not installed, open VS Code and choose **File → Open Folder**, then select the extracted `permission-delta` folder.

## Important

This is a local starter project, not yet a published GitHub repository or production security product. Do not use it as your only security control. Do not add real credentials to the example files.
