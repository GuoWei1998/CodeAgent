from pathlib import Path

WORKDIR = Path.cwd()

DENY_LIST = [
    "rm -rf /", "sudo", "shutdown", "reboot",
    "mkfs", "dd if=", "> /dev/sda",
]

PERMISSION_RULES = [
    {
        "tools": ["write_file", "edit_file"],
        "check": lambda args: not (WORKDIR / args.get("path", "")).resolve().is_relative_to(WORKDIR),
        "message": "Writing outside workspace",
    },
    {
        "tools": ["bash"],
        "check": lambda args: any(kw in args.get("command", "") for kw in ["rm ", "> /etc/", "chmod 777"]),
        "message": "Potentially destructive command",
    },
]

def ask_user(tool_name: str, args: dict, reason: str) -> str:
    print(f"\n⚠  {reason}")
    print(f"   Tool: {tool_name}({args})")
    choice = input("   Allow? [y/N] ").strip().lower()
    return "allow" if choice in ("y", "yes") else "deny"

def check_permission(block) -> bool:
    # 1、拒绝列表（针对bash工具的权限审批）
    if block.name == "bash":
        command = block.input.get("command", "")
        for denied in DENY_LIST:
            if denied in command:
                return "Permission denied by deny list"

    # 2、规则匹配
    reason = None
    for rule in PERMISSION_RULES:
        if block.name in rule["tools"]:
            if rule["check"](block.input):
                reason=rule["message"]
    # 3、用户审批
    if reason:
        decision=ask_user(block.name, block.input, reason)
        if decision == "deny":
            return "Permission denied by user"
        
    return None