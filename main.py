from anthropic import Anthropic
import os
import subprocess
from dotenv import load_dotenv

load_dotenv() #加载环境变量

api_key = os.getenv("ANTHROPIC_AUTH_TOKEN")
if not api_key:
    raise RuntimeError("Missing ANTHROPIC_AUTH_TOKEN environment variable")
client = Anthropic(
    api_key=api_key,
    base_url=os.getenv("ANTHROPIC_BASE_URL") or None,
)
MODEL = os.getenv("MODEL_ID")
if not MODEL:
    raise RuntimeError("Missing MODEL_ID environment variable")
MAX_STEPS = int(os.getenv("MAX_STEPS", "100"))
SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."
TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]

# Tools
def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def agent_loop(user_input, messages: list):
    step_count = 0
    # 1、整个Agent的上下文
    messages.append({"role": "user", "content": user_input})
    # 2、进入loop循环
    while True:
        # 3、调用LLM
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )
        # 4、把响应加入messages
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return

        # 5、执行工具调用
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # 执行工具调用
                print(f"\033[33m$ {block.input['command']}\033[0m")
                output = run_bash(block.input["command"])
                print(output[:200])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
                step_count += 1
                if step_count >= MAX_STEPS:
                    print("Error: Maximum steps reached")
                    return

        messages.append({"role": "user", "content": results})


        

def main():
    while True:
        # 1、获取输入
        user_input = input(">")
        if user_input == "quit" or user_input == "q":
            break
        # 2、进入Agent_loop
        history = []
        agent_loop(user_input, history)
        response_content = history[-1]["content"] if history else ""
        if isinstance(response_content, list):
            for block in response_content:
                if getattr(block, "type", None) == "text":
                    print(block.text)
        print()

if __name__ == "__main__":
    main()