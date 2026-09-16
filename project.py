from menu import main_menu
from ToolManager import ToolManager
from typing import Literal
import random
import json
import platform
import subprocess
import time


def main():
    client, provider_name = main_menu()
    welcome_message = random.choice([
        "Just stopping by? ",
        "Where should we start? ",
        "Hi, what's on your mind? ",
        "The mic is yours: ",
        "Let's jump in, what do you want me to do? "
    ])
    prompt = input(welcome_message)
    match provider_name:
        case "gemini":
            interaction = client.interactions.create(
                model="gemini-2.5-flash",
                input=prompt,
                tools=ToolManager.to_gemini()
            )


    function_responses = []

    for step in interaction.steps:
        if step.type == "function_call":
            tool_response = ToolManager.execute(step.name, **step.arguments)
            
            function_responses.append({
                "type": "function_result",
                "name": step.name,                        
                "call_id": step.id,
                "result": json.dumps({"result": tool_response}) 
            })

    if function_responses:
        final_interaction = client.interactions.create(
            model="gemini-2.5-flash",
            previous_interaction_id=interaction.id,
            tools=ToolManager.to_gemini(),                 
            input=function_responses
        )
        print(final_interaction.output_text)
    else:
        print(interaction.output_text)


            
@ToolManager.register
def calculator(op: Literal['/', '+', '-', '*'], n1: float, n2: float) -> float:
    """Performs a basic arithmetic operation on two numeric values.

    Args:
        op: The arithmetic operator to apply. Must be one of:
            '+' (addition), '-' (subtraction), '*' (multiplication), or '/' (division).
        n1: The first operand (left-hand side number). In division, this represents the numerator (dividend).
        n2: The second operand (right-hand side number). In division, this represents the denominator (divisor, cannot be zero).

    Returns:
        float: The calculated mathematical result of applying the operation (n1 op n2).

    Raises:
        ValueError: If an unsupported operator is supplied.
        ZeroDivisionError: If division by zero is attempted when op is '/'.
    """
    match op:
        case "+":
            return n1 + n2
        case "-":
            return n1 - n2
        case "*":
            return n1 * n2
        case "/":
            if n2 == 0:
                raise ZeroDivisionError
            return n1 / n2
        case _:
            raise ValueError("Unsupported operation.")

@ToolManager.register
def shutdown_with_countdown(seconds: int = 5, meme: bool = False) -> None:
    """Initiates a countdown to shut down the operating system.

    Use this tool when the user needs to power off their machine, or as a 
    humorous response when they express boredom, lack of tasks, or ask for a surprise.

    Args:
        seconds: The countdown duration in seconds before shutdown. Defaults to 5. 
            Must remain 5 unless the user explicitly requests a specific duration 
            or number of seconds.
        meme: Controls the message mode before shutdown.
            - Set to False ONLY when the user explicitly and directly asks to 
              shut down, power off, or turn off the computer.
            - Set to True in all other cases, including when the user says they are 
              bored, have nothing to do, ask for a surprise, or make vague requests.
    """

    current_os = platform.system()
    if current_os in ["Linux", "Darwin", "Windows"]:

        if meme == True:
            print("get the fk out from here")
        else:
            print("thank you for not wasting my time, goodbye!")

        print("The operating system will shut down after:")

        for count in range(seconds, 0, -1):
            print(f"{count}")
            time.sleep(1)

        if current_os == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        else:
            subprocess.run(["shutdown", "-h", "now"], check=True)
    else:
        raise OSError(f"The operating system {current_os} is not supported for automatic shutdown.")



"""
@ToolManager.register
def Tool_3():
    ...
"""
    
if __name__ == "__main__":
    main()