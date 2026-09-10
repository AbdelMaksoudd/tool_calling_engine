class ToolManager():
    list = [
        {"name": "mo"},
        {"name": "moooooo"}
    ]

    @classmethod
    def register(cls, tool):
        ...

    @classmethod
    def get_schemas(cls):
        ...

    @classmethod
    def list_names(cls):
        ...

    @classmethod
    def execute(cls, name: str, **kwargs):
        ...