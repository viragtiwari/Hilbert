from ast import parse
from tools.dir.file_exp import select_folder,is_folder_empty
from model import chat
from tools.memory.page_rank import CodeDependencyGraphGenerator
from tools.memory.repoMap import map_repository
from context_management import append_context,get_context
from tools.dir.writing import handle_commands_from_text 
from tools.dir.read_file import parse_file_list,read_files_from_paths
from tools.memory.dir_all_files import list_files_single_function
import prompts
import json
from pathlib import Path
from output_struct import repo_reader

#selecting the folder
selected_folder = select_folder()
generator = CodeDependencyGraphGenerator()

print(f"Selected folder: {selected_folder}")


#reading the repo_map.json file
def read_repo_map(file_path: str) -> dict:
    """
    Read and parse a repository map JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(file_path)
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


#chatting with the model
def chat_with_model(system,prompt,model):
    conversation = get_context()
    conversation.append({"role": "user", "content": prompt})
    append_context("user",prompt)   
    chat_response = chat(system,conversation,model)
    append_context("assistant",chat_response)
    return chat_response




def reader_agent(repo_map,model):
    conversation = []
    conversation.append({"role": "user", "content": f"""repo_map: {repo_map}
    output structure: {repo_reader} only reply in the given format and no other words
    """})
    chat_response = chat("You are an expert software engineer which can use repo map to navigate the repo and can ask for the relevant files to serve the user's demand",conversation,model)
    return chat_response
   


if is_folder_empty(selected_folder):
    print("No repo to scan")
else:
    print("Repo to scan:",selected_folder)
    print("Mapping repository...")
    map_repository(selected_folder)
    print("Generating graph...")
    generator.generate_graph(f"{selected_folder}/.lagrange/repo_map.json")




if __name__ == "__main__":
    if is_folder_empty(selected_folder):
        print("Selected folder is empty")
        while True:
            prompt = input("Enter your prompt: ")
            if prompt.lower() == "exit":
                break
            chat_response = chat_with_model(prompts.coding_prompt,f"Make code files, and you are in the parent directory: {prompt}","llama-3.3-70b-versatile")
            print(chat_response)
            handle_commands_from_text(chat_response,selected_folder)

    prompt = input("Enter your prompt: ")
    print("Reading the repo....")
    
    all_files_in_repo = list_files_single_function(selected_folder)
    print(f"Found {len(all_files_in_repo)} files in the repo")
    
    repo_map = read_repo_map(f"{selected_folder}/.lagrange/repo_map.json")
    files_to_read = reader_agent(f"List of all files in the repo: {all_files_in_repo} and repo_map:{repo_map} Now tell all the files to read for the task: {prompt} <Instruction>You are in the parent directory don't write it</Instruction>","llama-3.3-70b-versatile")
    print(f"Reader Agent: {files_to_read}")
    
    santized_files = parse_file_list(files_to_read)
    files = read_files_from_paths(selected_folder,santized_files)
    print(f"Reading the files: {files_to_read}")
    
    append_context("user", f"Use the repo_map: {repo_map} and help me with the following task {prompt}")
    
    append_context("assistant", f"""Using the repo_map, I want to read the following files: {files_to_read}
    Now I will complete the task
    """)
    
    append_context("user",f"Go on with the task {prompt}")
    
    chat_response = chat_with_model(prompts.coding_prompt,f"""{prompt}

files:
{files}


This is the wrong format 
example:
```css
// (styles/styles.css)
code:

but the correct is 
```css
(styles/styles.css)
code:""","llama-3.3-70b-versatile")
    print(chat_response)
    handle_commands_from_text(chat_response,selected_folder)
    
    while True:
        prompt = input("Enter your prompt: ")
        if prompt.lower() == "exit":
            break
        plan = chat_with_model(prompts.architect_prompt,prompt,"llama-3.3-70b-versatile")
        print(plan)
        files_to_read = reader_agent(f"List of all files in the repo: {all_files_in_repo} and repo_map:{repo_map} Now tell all the files to read for the task: {plan}","llama-3.3-70b-versatile")
        santized_files = parse_file_list(files_to_read)
        files = read_files_from_paths(selected_folder,santized_files)
        chat_response = chat_with_model(prompts.coding_prompt,f"""{plan}

files:
{files}

This is the wrong format 
example:
```css
// (styles/styles.css)
code:

but the correct is 
```css
(styles/styles.css)
code:""","llama-3.3-70b-versatile")
        print(chat_response)
        handle_commands_from_text(chat_response,selected_folder)

        