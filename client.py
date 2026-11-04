import time
import json
from pydantic import ValidationError
from ToolManager import ToolManager, ToolNotFoundError
from typing import Generator, Dict, Any, Literal
from litellm import (
    completion,
    AuthenticationError,
    RateLimitError,
    ContextWindowExceededError,
    ContentPolicyViolationError,
    NotFoundError,
    ServiceUnavailableError,
    APIConnectionError,
    Timeout
    )

# import litellm
# litellm.turn_on_debug()


def trim_messages(messages: list, trim_messages_num: int = 2):
    sys_messages = [message for message in messages if message.get("role") == "system"]
    another_messages = [message for message in messages if message.get("role") != "system"]

    del another_messages[0:trim_messages_num]

    while another_messages and another_messages[0].get("role") != "user":
        del another_messages[0]

    return sys_messages + another_messages




def stream(
        model: str,        
        messages: list,

        tools: list|None = None,
        max_retries: int = 3,
        trim_messages_num: int = 2,
        max_tool_iterations: int|Literal[True] = 5,
        timeout: float|int = 120.0
)-> Generator[Dict[str, Any], None, None]:

  
    retry_count: int = 0

    while retry_count < max_retries:
        retry_count +=1


        try:
            tool_iteration = 0
            while max_tool_iterations is True or tool_iteration < max_tool_iterations:
                if max_tool_iterations is not True:
                    tool_iteration += 1

                current_tools = tools
                if max_tool_iterations is not True and tool_iteration >= max_tool_iterations:
                    current_tools = None


                    
                response = completion(
                    model= model,
                    messages= messages,
                    tools=current_tools,
                    stream= True,
                    timeout= timeout
                )

                    
                tool_calls_dict = {}
                content = ""

                

                for chunk in response:
                    

                    if len(chunk.choices) == 0:
                        continue

                    choice = chunk.choices[0]
                    delta = choice.delta

                    if choice.finish_reason:
                        finish_reason = choice.finish_reason
                        


                    if delta.content:
                        content += delta.content
                        yield {"error_messages": None, "response_content": delta.content}
                    
                    


                
                    if delta.tool_calls:
                        

                        for tool_call in delta.tool_calls:

                            idx = tool_call.index
                            if idx not in tool_calls_dict:
                                tool_calls_dict[idx] = {
                                    "id": "",
                                    "type": "function",
                                    "function": {
                                        "name": "",
                                        "arguments": ""
                                    }    
                                }                

                            if tool_call.id:
                                tool_calls_dict[idx]["id"] += (tool_call.id or "")

                            if tool_call.function and tool_call.function.name:
                                tool_calls_dict[idx]["function"]["name"] += (tool_call.function.name or "")

                            if tool_call.function and tool_call.function.arguments:
                                tool_calls_dict[idx]["function"]["arguments"] += (tool_call.function.arguments or "")
                        
                        # print(tool_calls_dict)


                    
                assistant_message = {
                    "role": "assistant",
                    "content": content or None,
                }

                if tool_calls_dict:
                    assistant_message["tool_calls"] = list(tool_calls_dict.values())

                messages.append(assistant_message)


                if not tool_calls_dict:
                        return



                # yield {"error_messages": None, "response_content": f"\n[Executing tools...]\n"}

                tool_messages = []
                for call in tool_calls_dict.values():
                    tool_dic ={
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "name": call["function"]["name"]

                    }


                    try:
                        arg = json.loads(call["function"]["arguments"])
                        tool_dic["content"] = str(ToolManager.run(tool_name= call["function"]["name"], **arg))

                    except json.JSONDecodeError as e:   ################# catch uncompleate json from llm
                        tool_dic["content"] = f"Error: {e}"

                    except ToolNotFoundError as e:      ################ catch wrong tool name that came from llm
                        tool_dic["content"] = f"Error: {e}"

                    except ValidationError as e:        ################ catch wrong tool arguments that came from llm
                        tool_dic["content"] = f"Error: {e}"

                    except Exception as e:
                        tool_dic["content"] = f"Error executing tool: {e}"

                    tool_messages.append(tool_dic)


                messages.extend(tool_messages)
                # print(json.dumps(messages, indent=2))
         
                



    ############### exceptions:
    
        except RateLimitError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or retry_count >= max_retries:
                yield {"error_messages": "Error: Daily quota exceeded. Please try again tomorrow or upgrade your plan.", "response_content": None}
                return
            time.sleep(2 ** retry_count)



        except AuthenticationError:
            yield {"error_messages": "Error: Ensure that your API key is correct!", "response_content": None}
            return
        
        except NotFoundError:  #the model
            yield {"error_messages": "cant found that model", "response_content": None}
            return
        
        except ContentPolicyViolationError:
            yield {"error_messages": "watch your language", "response_content": None}
            return
        



        except ContextWindowExceededError:
            original_length = len(messages)
            messages[:] = trim_messages(messages, trim_messages_num=trim_messages_num)
            
            if len(messages) >= original_length:
                yield {"error_messages": "Error: Context window exceeded and cannot be trimmed further.", "response_content": None}
                return
            
            retry_count -= 1
            continue

        

        except (ServiceUnavailableError, APIConnectionError, Timeout):
            if retry_count >= max_retries:
                yield {"error_messages": "Temporary error: The model servers are busy or the internet connection is weak; please try again later.", "response_content": None}
                return
            time.sleep(2 ** retry_count)

        except Exception as e:
            if retry_count >= max_retries:
                yield {"error_messages": "Error: An unexpected event occurred", "response_content": None}
                return
            time.sleep(2 ** retry_count)