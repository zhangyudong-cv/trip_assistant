from typing import TypedDict, Annotated, Optional, Literal

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
    更新对话状态栈。
    参数:
        left (list[str]): 当前的状态栈。
        right (Optional[str]): 想要添加到栈中的新状态或动作。如果为 None，则不做任何更改；
                               如果为 "pop"，则弹出栈顶元素；否则将该值添加到栈中。
    返回:
        list[str]: 更新后的状态栈。
    """
    if right is None:
        return left  # 如果right是None，保持当前状态栈不变
    if right == "pop":
        return left[:-1]  # 如果right是"pop"，移除栈顶元素（即最后一个状态）
    return left + [right]  # 否则，将right添加到状态栈中


# 1. “维持原状”策略
# python
# if right is None:
#     return left
# 含义：如果节点返回了 None（或者没有针对这个字段返回任何值）。
# 结果：旧的栈 left 原封不动保留。
# 场景：主助手在查天气或闲聊，没有涉及到权限交接，所以当前的“专注焦点”不需要改变。
# 2. “退回上一层”策略 (Pop)
# python
# if right == "pop":
#     return left[:-1]
# 含义：如果节点明确返回了字符串 "pop"。
# 结果：利用 Python 的切片 [:-1] 删掉列表的最后一个元素。
# 场景：机票助手帮用户改签完了，它会返回一个 pop。比如原来的栈是 ['assistant', 'update_flight']，执行后就变回了 ['assistant']。这样对话主导权就回到了“老上级”主助手手里。
# 3. “权限委派”策略 (Push)
# python
# return left + [right]
# 含义：如果 right 是预设的助手名称（如 "update_flight"）。
# 结果：将这个新名称通过控制台追加到列表末尾。
# 场景：主助手对用户说“好的，我为您转接机票专家”。此时它会返回 "update_flight"，栈就从 ['assistant'] 变成了 ['assistant', 'update_flight']。

# 状态类
class State(TypedDict):
    """
    定义一个结构化的字典类型，用于存储对话状态信息。
    字段:
        messages (list[AnyMessage]): 使用 Annotated 注解附加了 add_messages 功能的消息列表，
                                     可能用于自动处理消息的某些方面。
        user_info (str): 存储用户信息的字符串。
        dialog_state (list[Literal["assistant", "update_flight", "book_car_rental",
                                    "book_hotel", "book_excursion"]]): 对话状态栈，限定只能包含特定的几个值，
                                    并使用 update_dialog_stack 函数来控制其更新逻辑。
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[  # Annotated 在这里的作用是：为变量绑定一个“更新规则”。
        list[  # 其元素严格限定为上述五个字符串值之一。这种做法确保了对话状态管理逻辑的一致性和正确性，避免了意外的状态值导致的潜在问题。
            Literal[
                "assistant",
                "update_flight",
                "book_car_rental",
                "book_hotel",
                "book_excursion",
            ]
        ],
        update_dialog_stack,
    ]



# 1. messages (对话历史)
# 类型：Annotated[list[AnyMessage], add_messages]
# 作用：存储用户和 AI 之间的所有对话记录。
# 特性：使用了 add_messages 装饰器。这意味着当某个节点返回新的消息时，LangGraph 不会覆盖旧的消息列表，而是**自动追加（Append）**到列表末尾。这是实现多轮对话的基础。
# 2. user_info (旅客个人信息)
# 类型：str
# 作用：存储通过 fetch_user_info 节点查询到的旅客实时信息（如航班号、姓名等）。
# 特性：这是一个普通的覆盖型字段。一旦获取了最新的旅客信息，它就会在整个工作流中共享，供各个子助手（如机票、租车助手）参考，而无需反复查询数据库。
# 3. dialog_state (对话状态栈)
# 这是最关键的设计，用于管理多智能体切换（Delegation）。

# 类型：Annotated[list[Literal[...]], update_dialog_stack]
# 作用：它是一个**栈（Stack）**结构，记录了当前哪个助手正在接管对话。
# 取值范围：限定在 assistant（主助手）、update_flight（机票）、book_car_rental（租车）、book_hotel（酒店）、book_excursion（旅游）这五个范围内。
# 工作机制 (update_dialog_stack)：
# 入栈：当主助手发现用户想买票，会将 update_flight 放入栈顶，此时工作流跳转到机票子流程。
# 退栈 ("pop")：当子任务完成后，由于标记了 pop，状态会返回到上一层（主助手），就像函数调用返回一样。
# 特性：这保证了 Agent 知道“我在哪里”以及“任务完成后该回哪去”。