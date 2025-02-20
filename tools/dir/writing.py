import re
import os
import subprocess
import sys
import platform

def run_command(command):
    """Run a shell command and handle output and errors with improved debugging."""
    #print(f"Executing command: {command}")  # Debug line to show what command is being run
    
    try:
        # Create process with pipes for both stdout and stderr
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output and error streams in real-time
        while True:
            # Read one line from stdout
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(f"STDOUT: {stdout_line.strip()}")
            
            # Read one line from stderr
            stderr_line = process.stderr.readline()
            if stderr_line:
                print(f"STDERR: {stderr_line.strip()}")
            
            # Check if process has finished
            if process.poll() is not None:
                # Read any remaining output
                remaining_stdout, remaining_stderr = process.communicate()
                if remaining_stdout:
                    print(f"STDOUT: {remaining_stdout.strip()}")
                if remaining_stderr:
                    print(f"STDERR: {remaining_stderr.strip()}")
                break
        
        # Check return code after process completion
        if process.returncode != 0:
            print(f"Command failed with return code: {process.returncode}")
            return False
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while running command '{command}': {str(e)}")
        return False

def handle_commands_from_text(text, actual_path):
    """Parse the provided text and handle code blocks and shell commands.
    
    Args:
        text (str): The text to parse for commands
        actual_path (str): The directory where code will be saved
    """
    # Define supported programming languages
    supported_languages = [
        'python', 'javascript', 'js', 'c++', 'cpp', 'c', 'html', 'css', 'dart', 'java', 'ruby', 'go', 'typescript', 'php', 'swift', 'kotlin','markdown','json','GIT', 'yaml','xml','tsx','text'
    ]
    supported_shells = [
        'shell', 'sh', 'ps1', 'bash','cmd', 'bat', 'vbs', 'ksh'
    ]
    
    # Create regex patterns for supported languages
    languages_pattern = '|'.join([re.escape(lang) for lang in supported_languages])
    python_pattern = rf"```({languages_pattern})\s*\n\((.+?)\)\ncode:\s*(.*?)```"
    shells_pattern = '|'.join([re.escape(lang) for lang in supported_shells])
    shell_pattern = rf"```({shells_pattern})\s*\n\((.+?)\)\ncode:\s*(.*?)```"

    python_matches = re.findall(python_pattern, text, re.DOTALL | re.IGNORECASE)
    shell_matches = re.findall(shell_pattern, text, re.DOTALL | re.IGNORECASE)

    if not python_matches and not shell_matches:
        return

    passpath = ""
    # Handle code blocks for supported languages
    for language, relative_path, code in python_matches:
        filepath = os.path.join(actual_path, relative_path)
        passpath = relative_path
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(code.strip())

    # Handle shell commands
    for language, relative_path, command in shell_matches:
        shell_file_name = "commands.bat" if sys.platform == 'win32' else "commands.sh"
        shell_file_path = os.path.join(actual_path, shell_file_name)
        
        with open(shell_file_path, 'w') as shell_file:
            if sys.platform != 'win32':
                shell_file.write("#!/bin/bash\n")
            for commands in command:
                shell_file.write(commands.strip())

        if sys.platform != 'win32':
            os.chmod(shell_file_path, 0o755)
        run_command(f'"{shell_file_path}"')
    
    # Return the first segment of the path if it contains subdirectories
    passpath = passpath.split("/")[0] if passpath else ""
    return passpath