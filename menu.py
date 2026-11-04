from ToolManager import ToolManager
from questionary import Choice
import questionary
import sys
import warnings


def main_menu():

    while True:
        choice = questionary.select(
        """=====================================================
    Agentic Tool-Calling Engine & Runtime v1.0       
=======================================================\n""",
        choices=[
            Choice("[1] Interactive Playground (Manual testing and inspection of tools)", value="playground"),
            Choice("[2] Live Agent Mode (Connecting the engine to LLM model API)", value="agent_mode"),
            Choice("[*] Exit", value="exit")
        ]).ask()

        match choice:
            case "playground":
                handle_playground_flow()
            case "agent_mode":
                model= handle_live_agent_flow()
                if model:
                    return model
            case "exit" | None:
                sys.exit("thank you for not wasting my time")

            
    

def handle_playground_flow():
    while True:
        functions = [tool for tool in ToolManager.tools_dict]  #function["tool_details"]["name"] must be one word
        choice = questionary.select(
        "Please select the function you would like to try.",
        choices=(
            [Choice(f"[{i}] {function}", value=function, disabled= True) for i, function in enumerate(functions)]+
            [Choice("[*] Back", value="back")]
            )).ask()

        match choice:
            case "back":
                return
            case None:
                sys.exit("thank you for not wasting my time")
            

def handle_live_agent_flow():
    while True:

        selected_provider = questionary.select(
            "Which AI provider will you use?",
            choices=[
                Choice("[1] Google Gemini API", value=("gemini/", "gemini-2.5-flash")),
                Choice("[2] OpenAI API", value=("", "gpt-4o-mini")),
                Choice("[3] Anthropic Claude API", value=("", "claude-3-haiku-20240307")),
                Choice("[4] Hugging Face API", value=("huggingface/", "HuggingFaceH4/zephyr-7b-beta")),
                Choice("[5] Groq API", value=("groq/", "llama3-8b-8192")),                
                Choice("[6] Ollama (Local)", value=("ollama/", "mistral")),                
                Choice("[*] Back", value="back"),   
            ]).ask()

        match selected_provider:
            case None:
                sys.exit("thank you for not wasting my time")
            case "back":
                return None 
            
            case (prefix, default_model):
                
                model_choice = questionary.select(
                    "Do you want to use the default model or type a custom one?",
                    choices=[
                        Choice(f"Use default: {default_model}", value="default"),
                        Choice("Type a custom model name", value="custom"),
                        Choice("Cancel / Go Back", value="back")
                    ]).ask()

                if model_choice is None:
                    sys.exit("thank you for not wasting my time")
                elif model_choice == "back":
                    continue
                
                final_model = ""
                
                if model_choice == "default":
                    final_model = f"{prefix}{default_model}"
                else:
                    custom_model = questionary.text("Enter the custom model name:").ask()
                    
                    if custom_model is None:
                        sys.exit("thank you for not wasting my time")
                        
                    if prefix and custom_model.startswith(prefix):
                        final_model = custom_model
                    else:
                        final_model = f"{prefix}{custom_model}"
                
                return final_model

if __name__ == "__main__":
    main_menu()