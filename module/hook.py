# 注册hook
HOOKS = {
    "UserPromptSubmit": [],
    "PreToolUse": [],
    "PostToolUse": [],
    "Stop": [],
}

def register_hook(hook_type, func):
    if hook_type in HOOKS:
        HOOKS[hook_type].append(func)
    else:
        raise ValueError(f"Invalid hook type: {hook_type}")

def trigger_hook(hook_type, *args):
    for func in HOOKS[hook_type]:
        result = func(*args)
        if result is not None:
            return result
    return None

# PreToolUse: 日志
def log_hook(block):
    print(f"[HOOK] {block.name}(...)")

# PostToolUse: 大文件提醒
def large_output_hook(block, output):
    if len(str(output)) > 100000:
        print(f"[HOOK] ⚠ Large output from {block.name}")