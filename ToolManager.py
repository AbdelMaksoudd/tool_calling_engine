import inspect
from typing import get_type_hints, Any
from pydantic import BaseModel, create_model, Field, ValidationError
from docstring_parser import parse
import json


class ToolNotFoundError(Exception):
    pass

class ToolManager():
    
    def __init__(self, tool, input_validation, return_annotation, typ, description, name):
        self._tool = tool
        self._input_validation = input_validation
        self.return_annotation = return_annotation
        self.typ = typ    #-> type
        self.description = description
        self.name = name
        

    tools_dict = {}    #[{name: object(ToolManager)}]



    @classmethod
    def register(cls, tool):
        if inspect.isclass(tool) or not callable(tool):
            raise TypeError(f"Expected a function, got {type(tool)}")
        

        hints = get_type_hints(tool)
        return_annotation = hints.pop("return", None)

        sign = inspect.signature(tool)
        doc = parse(tool.__doc__ or "")
        parameters_description = {param.arg_name: param.description for param in doc.params}

        input_parameters = {}
        for name, param in sign.parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD): #skip *args, **kwargs
                continue
            default = ... if param.default == inspect.Parameter.empty else param.default
            annotation = hints.get(name, Any)
            input_parameters[name] = (annotation, Field(default= default, description= parameters_description.get(name, "")))
        
        
        input_validation = create_model(f"{tool.__name__}_schema", **input_parameters)
        tool_object = ToolManager(
            input_validation= input_validation,
            return_annotation= return_annotation,
            typ = "function",                     #-> type
            description= f"{doc.short_description}\n{doc.long_description}",
            tool= tool,
            name= tool.__name__
            )
        

        cls.tools_dict[tool.__name__] = tool_object
        return tool
      



    
    @classmethod
    def get_tools(cls):
        return [tool for tool in cls.tools_dict]

    @classmethod
    def run(cls, tool_name, **kwargs) -> ToolNotFoundError | ValidationError | Any | None:
        try:
            tool_object = cls.tools_dict[tool_name] 
        except Exception:
            raise ToolNotFoundError(tool_name)

        input_validation = tool_object._input_validation
        validation = input_validation(**kwargs)
        
        
        return tool_object._tool(**validation.model_dump())


    @classmethod
    def get_tool_schema(cls, tool_name):
        try:
            tool_object = cls.tools_dict[tool_name] 
        except Exception:
            raise ToolNotFoundError(tool_name)
        input_parameters_schema_dict = tool_object._input_validation.model_json_schema().get("properties", None)
        schema = {
            "type": tool_object.typ,
            "function": {
                "name": tool_object.name,
                "description": tool_object.description,
                "parameters": {
                    "type": "object",
                    "properties": input_parameters_schema_dict,
                    "required": [param for param in input_parameters_schema_dict if input_parameters_schema_dict[param].get("default")  == None]
                              }}}
        return schema

    @classmethod
    def get_all_schemas(cls):
        return [cls.get_tool_schema(tool) for tool in cls.tools_dict]



# def calculate_discount(price: float , discount_rate: float = 0, is_member: bool = False) -> float:
#     """
#     jjjjjjjjjjjjjjjjjjjjjj
#     hhhhhhhhhhhhhhhhhhhhhhh

#     :param price: jjjjjjjjjjjj
#     :param discount_rate: jjjjjjjjjjjjj
#     :param is_member: jjjjjjjjjjjjjjjjj
#     :return: jjjjjjjjjjj
#     """
#     print("doneeeeeeeeeeeeeee")

# ToolManager.register(calculate_discount)

# objecttt = ToolManager.tools_dict["calculate_discount"]._input_validation(price= 0, discount_rate= 0)
# print(json.dumps(ToolManager.get_all_schemas(), indent=2))



# # ToolManager.run("calculate_discount", price=1, discount_rate=1)