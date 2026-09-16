import inspect
from typing import Literal, get_args, get_origin
class ToolManager():
    
    json_schema = [
        {
            "tool_details": {"type": "function", "name": "name", "description": "description"},
            "argument_details":{
                "arguments":{
                    "arg1": {"type": "type", "description": "description", "enum": [1,2]},
                    "arg2": {"type": "type", "description": "description", "default": "default"},
                    "arg3": {"type": "array", "description": "description", "items":{"type": "string"}}        
                    },
                "required":["arg1", "arg2", "arg3"]

            }

                         
         }
    ]

    map_types = {
        "int": "integer",
        "float": "number",
        "str": "string",
        "dict": "object",
        "list": "array",
        "bool": "boolean"
    }

    tools = []
    _functions = {}



    @classmethod
    def register(cls, tool):
        if inspect.isclass(tool) or not callable(tool):
            raise TypeError(f"Expected a function, got {type(tool)}")
        dic = {}
        dic["tool_details"] = {}
        dic["argument_details"] = {}
        dic["tool_details"]["type"] = "function"
        dic["tool_details"]["name"] = tool.__name__
        dic["tool_details"]["description"] = inspect.getdoc(tool)
        args = {}
        required = []
        parameters = inspect.signature(tool).parameters
        for name, param in parameters.items():
            args[name] = {}
            
            if param.annotation != inspect.Parameter.empty:
                if not(get_origin(param.annotation) is Literal):
                    if hasattr(param.annotation, "__name__") and param.annotation.__name__ in cls.map_types:
                        typ = cls.map_types[param.annotation.__name__]

                    else:  
                        typ =""

                else: #object ex: Literal
                    args[name]["enum"] = list(get_args(param.annotation))
                    typ = cls.map_types[f"{type(args[name]['enum'][0]).__name__}"]

            else:
                typ = "unknown"



            args[name]["type"] = typ
            
            if param.default != inspect.Parameter.empty:
                args[name]["default"] = param.default
            else:
                required.append(name)

        dic["argument_details"]["arguments"] = args
        dic["argument_details"]["required"] = required

        cls.tools.append(dic)
        cls._functions[tool.__name__] = tool

    

    @classmethod
    def to_dict(cls): #get_schemas
        ...

    @classmethod
    def tool_names(cls):
        ...

    @classmethod
    def execute(cls, name: str, **kwargs):
        if name not in cls._functions:
            raise ValueError(f"Tool {name} not found")
        return cls._functions[name](**kwargs)

    @classmethod
    def to_gemini(cls):
        tools = []
        for tool in cls.tools:
            dic = {}
            dic["type"] = tool["tool_details"]["type"]
            dic["name"] = tool["tool_details"]["name"]
            dic["description"] = tool["tool_details"]["description"]
            dic["parameters"] = {}
            dic["parameters"] ["type"] = "object"
            dic["parameters"] ["properties"] = tool["argument_details"]["arguments"]
            dic["parameters"] ["required"] = tool["argument_details"]["required"]
            tools.append(dic)
        return tools 