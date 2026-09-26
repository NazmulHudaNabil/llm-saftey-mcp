from mcp.server.mcpserver import MCPServer
from . import safety

mcp = MCPServer("llm-safety")

@mcp.tool()
def check_prompt(text: str) -> str:
    """Checks a user prompt for safety issues like prompt injection."""
    return safety.detect_prompt_injection(text).model_dump_json(indent=2)

@mcp.tool()
def detect_pii(text: str) -> str:
    """Detects PII entities in the text (e.g. Email, Phone)."""
    return safety.detect_pii(text).model_dump_json(indent=2)

@mcp.tool()
def sanitize_text(text: str) -> str:
    """Redacts PII from the provided text."""
    return safety.sanitize_text(text)

@mcp.tool()
def check_response(text: str) -> str:
    """Checks an AI response for safety issues (e.g., leaking PII or secrets)."""
    return safety.check_text(text).model_dump_json(indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
