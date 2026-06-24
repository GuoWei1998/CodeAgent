# 学习路径
看文档->自己复述总结一遍->绘制架构图->重写->AI review->开源实现
# 笔记
## Agent loop
### 架构图

```mermaid
flowchart TD
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
    classDef tool fill:#fff7ed,stroke:#f97316,stroke-width:2px,color:#7c2d12;
    classDef final fill:#ecfdf5,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef loop fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155;

    class Start user;
    class Messages,LLM model;
    class Decision decision;
    class Tool,Append tool;
    class Final final;
    class Loop loop;
```

核心：一个 `while True` 循环里，模型判断要不要调用工具；如果要，就执行工具并把 `tool_result` 放回 `messages`，再进入下一轮；如果不要，就返回最终结果。
