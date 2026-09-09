import questionary
from questionary import Choice
import sys
from .functions import Functions
import re

class Menu():
    def __init__(self):
        ...
    @classmethod
    def main(cls):
        
        choice = questionary.select(
        """=====================================================
    Agentic Tool-Calling Engine & Runtime v1.0       
=======================================================\n""",
        choices=[
            "[1] Interactive Playground (Manual testing and inspection of tools)",
            "[2] Live Agent Mode (Connecting the engine to LLM model API)",
            "[*] Exit"
        ]).ask()

        if "[*] Exit" == choice:
            sys.exit("thank you for not wasting my time")
        elif "[1]" in choice:
            cls.one()
        elif "[2]" in choice:
            cls.two()

    @classmethod
    def one(cls):
        fuctions = [function["name"] for function in Functions.json]
        choice = questionary.select(
        "Please select the function you would like to try.",
        choices=([f"[{i}] {function}" for i, function in enumerate(fuctions)]+["[*] Back"])).ask()

        if "[*] Back" == choice:
            cls.main()



    @classmethod
    def two(cls):
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

        if "back" == selected_model:
            cls.main()
        else:
            api_key = questionary.password("please enter your api key: ").ask()
            
            print ({"name": selected_model,"api_key": api_key})
            
