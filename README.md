# Hilbert: Codebase Interaction Agent

## Description

Hilbert is a powerful codebase interaction agent designed to assist users with a variety of code-related tasks. Leveraging the capabilities of large language models, Hilbert can analyze code repositories, generate new code snippets, modify existing code, and provide detailed explanations of code functionality. It is designed to be a helpful assistant for software developers, enabling them to automate and streamline various development tasks. The repository mapping feature is inspired by Aider.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the Groq API key:**

    *   Obtain a Groq API key from [https://console.groq.com/](https://console.groq.com/).
    *   Set the `GROQ_API_KEY` environment variable. You can do this by creating a `.env` file in the project directory with the following content:

        ```
        GROQ_API_KEY=<your_groq_api_key>
        ```

## Modules

*   **`main.py`**: The central script orchestrating the application's functionality. 
    *   **Folder Selection**: Allows users to select a codebase directory via a GUI dialog.
    *   **Repository Mapping**: Utilizes `repoMap.py` to index code structure and symbols.
    *   **Dependency Graph Generation**: Employs `page_rank.py` to create a graph of code dependencies for analysis.
    *   **Language Model Interaction**: Integrates with `model.py` to handle conversations, code generation, and task execution using prompts from `prompts.py`.
    *   **File Reading and Command Execution**: Uses `read_file.py` and `writing.py` to interact with the file system and execute shell commands.

*   **`model.py`**: Manages interactions with the Groq language model API.
    *   **`chat()` function**: Sends prompts and conversation history to the Groq API and retrieves model responses.
    *   **API Key Handling**: Loads the Groq API key from environment variables for secure access.

*   **`prompts.py`**: Defines various prompts used to guide the language model for different tasks.
    *   **`conversation_prompt`**: Sets the tone and role for general conversations.
    *   **`coding_prompt`**: Instructs the model for code generation tasks, emphasizing file management, command execution, and code implementation guidelines.
    *   **`edit_prompt`**: Guides the model for code editing tasks, focusing on production quality, error handling, documentation, and testing.
    *   **`architect_prompt`**: Defines the role of an architect engineer to provide high-level instructions for code modifications.

*   **`context_management.py`**: Handles conversation context and history.
    *   **Context Storage**: Uses lists to store chat history and conversation context.
    *   **Context Summarization**: Employs the language model to summarize long conversations, keeping the context concise and relevant.
    *   **Context Appending and Retrieval**: Functions to append new messages to the context and retrieve the current context for model interactions.

*   **`output_struct.py`**: Specifies expected output formats.
    *   **`repo_reader`**: Defines the JSON format for repository file lists, ensuring structured output from the model.

*   **`tools/`**: A directory containing utility modules that extend Hilbert's capabilities.
    *   **`tools/dir/file_exp.py`**: Provides GUI-based file system exploration.
        *   **`select_folder()`**: Opens a dialog for folder selection.
        *   **`is_folder_empty()`**: Checks if a selected folder is empty.
    *   **`tools/dir/read_file.py`**: Implements file reading functionalities.
        *   **`parse_file_list()`**: Parses string representations of file lists.
        *   **`read_files_from_paths()`**: Reads and retrieves content from multiple files.
    *   **`tools/dir/writing.py`**: Manages file writing and command execution.
        *   **`run_command()`**: Executes shell commands and captures output.
        *   **`handle_commands_from_text()`**: Parses text for code and shell commands, then executes them.
    *   **`tools/memory/dir_all_files.py`**: Provides file system indexing.
        *   **`list_files_single_function()`**: Recursively lists all files in a directory, excluding specified patterns.
    *   **`tools/memory/page_rank.py`**: Implements code dependency analysis using PageRank.
        *   **`CodeDependencyGraphGenerator`**: Class to generate code dependency graphs, calculate PageRank, and identify important functions.
    *   **`tools/memory/repoMap.py`**: Implements repository mapping functionalities.
        *   **`FileMap`**: Data class to represent file paths and symbols.
        *   **`LanguageParser`**: Parses code files to extract symbols based on language-specific patterns.
        *   **`RepoMapper`**: Generates a comprehensive repository map by indexing files and symbols.

## Usage

Hilbert is designed to be interactive and driven by user prompts. Here’s how to use it:

1.  **Run the `main.py` script:**

    Open your terminal, navigate to the Hilbert project directory, and execute:

    ```bash
    python main.py
    ```

2.  **Select a Project Folder:**

    Upon starting, Hilbert will prompt you to select a project folder. This should be the root directory of the codebase you want to work with. Use the GUI file dialog to select the folder.

3.  **Initial Repository Scan:**

    Once a folder is selected, Hilbert automatically scans the repository. 
    *   **Repository Mapping**: It creates a `repo_map.json` in a `.Hilbert` directory within your project. This map indexes all files and code symbols in your repository, allowing Hilbert to understand your codebase structure.
    *   **Dependency Graph**: It generates a `concise.json` file, also in the `.Hilbert` directory, which contains a dependency graph of your code. This graph helps Hilbert understand the relationships between different parts of your code.

4.  **Interact with the Agent via Prompts:**

    After the repository scan, Hilbert will present a command prompt in your terminal: `Enter your prompt:`. 
    Here, you can enter various prompts to interact with Hilbert. Examples include:

    *   **Code Generation**: `Create a simple "Hello, world!" program in Python.`
    *   **Code Explanation**: `Explain the function 'read_files_from_paths' in detail.`
    *   **Code Modification**: `Modify the 'chat' function in 'model.py' to use a higher temperature.`
    *   **Task Planning**: `Plan the implementation of a new feature that adds user authentication to the application.`

5.  **Agent Responses and Actions:**

    Hilbert processes your prompts and responds in the terminal. 
    *   **Code Output**: If you ask for code generation or modification, Hilbert will output code blocks in the specified format.
    *   **Explanations**: For explanation prompts, Hilbert will provide detailed descriptions in plain text.
    *   **File Interactions**: Hilbert might read relevant files from your repository to understand the context of your request. It will indicate which files it is reading.
    *   **Command Execution**: In some cases, Hilbert might suggest or execute shell commands (e.g., to create files or install dependencies). It will clearly indicate when it is executing commands.

6.  **Iterative Interaction:**

    Hilbert maintains a conversation history, allowing for iterative refinement of tasks. You can continue to enter prompts to further guide Hilbert, ask follow-up questions, or modify your requests based on the agent's responses.

### Example

To ask the agent to create a simple "Hello, world!" program in Python, you can enter the following prompt:

```
Create a simple "Hello, world!" program in Python.
```

Hilbert will then generate the Python code and save it to a file (e.g., `hello.py`) in your selected project directory. You can then run this program directly from your terminal.

## Roadmap

Will update the roadmaps soon!

## Credits

The repository mapping feature in Hilbert is inspired by the [Aider](https://aider.chat/) project. We acknowledge and appreciate the work of the Aider team in developing this innovative feature.
