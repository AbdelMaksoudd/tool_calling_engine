from ToolManager import ToolManager
from questionary import Choice
import questionary
import sys
from providers.gemini import Gemini
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
                client, provider_name= handle_live_agent_flow()
                if client:
                    return client, provider_name
            case "exit" | None:
                sys.exit("thank you for not wasting my time")

            
    

def handle_playground_flow():
    while True:
        functions = [function["tool_details"]["name"] for function in ToolManager.tools]  #function["tool_details"]["name"] must be one word
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
        selected_model = questionary.select(
            "which AI model you use?",
            choices=[
                Choice("[1] Google Gemini API", value="gemini"),
                Choice("[2] OpenAI API", value="open_ai", disabled= True),
                Choice("[3] Anthropic Claude API", value="claude", disabled= True),
                Choice("[4] Hugging Face Inference API", value="hugging_face", disabled= True),
                Choice("[5] Groq API", value="groq", disabled= True),
                Choice("[6] Ollama (locally on your own computer)", value="ollama", disabled= True),
                Choice("[*] Back", value="back"),   
            ]).ask()


        match selected_model:
            case None:
                sys.exit("thank you for not wasting my time")
            case "back":
                return
            case _:
                try:
                    api_key = questionary.password("please enter your api key: ").ask()
                    if (api_key == None) or(type(api_key)==str and api_key.strip() == ""):
                        sys.exit("thank you for not wasting my time")

                except KeyboardInterrupt:
                    sys.exit("thank you for not wasting my time")

                match selected_model:
                    case "gemini":
                        gemini_object = Gemini(api_key)
                        if gemini_object.validation:
                            return gemini_object.client ,"gemini"
                        else:
                            print(f"\n[ERROR] Authentication Failed: {gemini_object.msg}\n")
                            questionary.press_any_key_to_continue().ask()
        
    
    


if __name__ == "__main__":
    main_menu()