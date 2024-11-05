

class Tool:
    def __init__(self, name, toolset):
        self.name = name
        self.tool_set = toolset
        self.tools = self._initialize_tools(toolset)

    def _initialize_tools(self, toolset):
        return {tool["name"]: tool for tool in toolset}

    def get_tool_schema(self):
        return self.tools.get(self.name)

    def anthropic_transform(self, tool):
        if "parameters" in tool:
            tool["input_schema"] = tool.pop("parameters")
        elif "toolSpec" in tool:
            tool["input_schema"] = tool.pop("toolSpec")
        return tool

    def openai_transform(self, tool):
        if "input_schema" in tool:
            tool["parameters"] = tool.pop("input_schema")
        elif "inputSchema" in tool:
            tool["parameters"] = tool.pop("inputSchema")
        elif "toolSpec" in tool:
            tool["parameters"] = tool.pop("toolSpec")
        elif "parameters" in tool:
            tool["parameters"] = tool.pop("parameters")
        else:
            raise ValueError(f"Model not supported")
        return tool
    
    @property
    def __dict__(self):
        return {
            "name": self.name,
            "toolset": self.tool_set
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)