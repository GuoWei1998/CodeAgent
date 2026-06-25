# 学习路径
看文档->自己复述总结一遍->绘制架构图->重写()->AI review->开源实现
# 笔记
## Agent loop
### 架构图

```mermaid
flowchart LR
    Start["用户提问<br/>帮我创建 hello.py"] --> Messages["messages[]<br/>累积式消息列表"]
    Messages --> LLM["大模型 LLM<br/>读取消息历史<br/>判断是否需要工具<br/>返回 stop_reason"]
    LLM --> Decision{"stop_reason<br/>== tool_use ?"}

    Decision -- "否" --> Final["返回结果<br/>循环结束"]
    Decision -- "是" --> Tool["执行工具调用<br/>run_bash(command)"]
    Tool --> Append["追加 tool_result 到 messages"]
    Append -. "进入下一轮循环" .-> Messages

    subgraph Loop["Agent Loop: 一个 while 循环驱动整个 Agent"]
        Messages
        LLM
        Decision
        Tool
        Append
    end

    classDef user fill:#eef4ff,stroke:#2563eb,stroke-width:2px,color:#172554;
    classDef model fill:#f8fbff,stroke:#2563eb,stroke-width:2px,color:#172554;
    classDef decision fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    classDef new fill:#ecfdf5,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef loop fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155;

    class Start,Final user;
    class Messages,LLM,Tool,Append model;
    class Decision decision;
    class Loop loop;
```

核心：一个 `while True` 循环里，模型判断要不要调用工具；如果要，就执行工具并把 `tool_result` 放回 `messages`，再进入下一轮；如果不要，就返回最终结果。

## Tool Use
### 架构图
```mermaid
flowchart LR
    Start["用户提问<br/>帮我创建 hello.py"] --> Messages["messages[]<br/>累积式消息列表"]
    Messages --> LLM["大模型 LLM<br/>读取消息历史<br/>判断是否需要工具<br/>返回 stop_reason"]
    LLM --> Decision{"stop_reason<br/>== tool_use ?"}

    Decision -- "否" --> Final["返回结果<br/>循环结束"]
    Decision -- "是" --> ToolSet
    ToolSet --> Append["追加 tool_result 到 messages"]
    Append -. "进入下一轮循环" .-> Messages

    subgraph Loop["Agent Loop: 一个 while 循环驱动整个 Agent"]
        Messages
        LLM
        Decision
        ToolSet
        Append
    end

    subgraph ToolSet["Tool Dispatch"]
        bash
        read_file
        write_file
        edit_file
    end

    classDef user fill:#eef4ff,stroke:#2563eb,stroke-width:2px,color:#172554;
    classDef model fill:#f8fbff,stroke:#2563eb,stroke-width:2px,color:#172554;
    classDef decision fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    classDef new fill:#ecfdf5,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef loop fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155;

    class Start,Final user;
    class Messages,LLM,Tool,Append model;
    class Decision decision;
    class ToolSet new;
    class Loop loop;
```
核心：将bash工具扩展到4个工具的工具集