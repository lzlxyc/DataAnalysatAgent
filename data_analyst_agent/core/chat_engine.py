import json
from pprint import pprint

from .messages import (
    ChatMessages,
    MessageType,
    MessageDict
)

from ..api import LlmBox
from ..utils.helpers import (
    modify_prompt,
    add_task_decomposition_prompt,
    function_to_call
)

def get_deepseek_response(
        llm_api:LlmBox,
        messages:ChatMessages,
        available_functions=None,
        is_developer_mode=False,
        is_enhanced_mode=False) -> MessageType:
    """
    负责调用Chat模型并获得模型回答函数，并且当在调用GPT模型时遇到Rate limit时可以选择暂时休眠1分钟后再运行。\
    同时对于意图不清的问题，会提示用户修改输入的prompt，以获得更好的模型运行结果。
    :param llm_api: 必要参数，实例化后的大模型调用接口
    :param model: 必要参数，表示调用的大模型名称
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :return: 返回模型返回的response message
    """

    # 如果开启开发者模式，则进行提示词修改，首次运行是增加提示词
    if is_developer_mode:
        messages = modify_prompt(messages, action='add')

    # 如果是增强模式，则增加复杂任务拆解流程
    # if is_enhanced_mode:
    #     messages = add_task_decomposition_prompt(messages)

    # 若不存在外部函数
    if available_functions is None:
        response = llm_api.chat(messages=messages.messages)
    else:
        response = llm_api.chat(
        messages=messages.messages,
        tools=available_functions.functions)

    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(messages.messages[-3:])
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    # 关键步骤，首次加入了cot后，进行删除
    if is_developer_mode:
        modify_prompt(messages, action='remove')

    return response


def check_get_final_function_response(
        llm_api:LlmBox,
        messages:ChatMessages,
        function_call_message:MessageType,
        function_response_message:MessageDict,
        available_functions=None,
        is_developer_mode=False,
        is_enhanced_mode=False,
        delete_some_messages=True
):
    '''负责执行外部函数运行结果审查工作。若外部函数运行结果消息function_response_message并不存在报错信息，\
    则将其拼接入message中，并将其带入get_chat_response函数并获取下一轮对话结果。而如果function_response_message中存在报错信息，\
    则开启自动debug模式。本函数将借助类似Autogen的模式，复制多个Agent，并通过彼此对话的方式来完成debug。
    '''
    # 获取外部函数运行的结果内容
    fun_res_content = function_response_message['content']

    # 如果包含报错信息，就调用debug功能
    if "报错" in fun_res_content:
        print(f'报错信息：{fun_res_content}')
        # 根据是否开启增强模式，选择执行开启高效debug还是深度debug
        if not is_enhanced_mode:
            # 执行高效debug
            debug_info = "**即将执行高效debug，正在实例化Efficient Debug Agent...**"
            debug_prompt_list = ['你编写的代码报错了，请根据报错信息修改代码并重新执行。']
        else:
            debug_info = "**即将执行深度debug，该debug过程将自动执行多轮对话，请耐心等待。正在实例化Deep Debug Agent...**"
            debug_prompt_list = [
                "之前执行的代码报错了，你觉得代码哪里编写错了？",
                "好的。那么根据你的分析，为了解决这个错误，从理论上来说，应该如何操作呢？",
                "非常好，接下来请按照你的逻辑编写相应代码并运行。"
            ]

        print(debug_info)

        msg_debug = messages.copy()
        # 追加function_call_message和包含报错信息的function_call_message
        msg_debug.messages_append(function_call_message)
        msg_debug.messages_append(function_response_message)

        # 依次输入debug的prompt来引导大模型进行debug
        for debug_prompt in debug_prompt_list:
            msg_debug.messages_append({'role':'user','content':debug_prompt})

            print(f"**From Debug Agent:**\n{debug_prompt}")
            print("**From MateGen:**")
            msg_debug = get_chat_response(
                llm_api=llm_api,
                messages=msg_debug,
                available_functions=available_functions,
                is_developer_mode=is_developer_mode,
                is_enhanced_mode=False,
                delete_some_messages=delete_some_messages
            )
        messages = msg_debug.copy()

    # 如果不包含报错信息，直接将结果传给大模型
    else:
        print(">>> 外部函数已执行完毕，正在解析运行结果...", function_call_message)
        messages.messages_append(function_call_message)
        messages.messages_append(function_response_message)
        messages = get_chat_response(
            llm_api=llm_api,
            messages=messages,
            available_functions=available_functions,
            is_developer_mode=is_developer_mode,
            is_enhanced_mode=is_enhanced_mode,
            delete_some_messages=delete_some_messages
        )
    return messages


def is_text_response_valid(
        llm_api:LlmBox,
        messages:ChatMessages,
        text_answer_message:MessageType,
        available_functions=None,
        is_developer_mode=False,
        is_enhanced_mode=False,
        delete_some_messages=False,
        is_task_decomposition=False
):

    """
    负责执行文本内容创建审查工作。运行模式可分为快速模式和人工审查模式。在快速模式下，模型将迅速创建文本并保存至msg对象中，\
    而如果是人工审查模式，则需要先经过人工确认，函数才会保存大模型创建的文本内容，并且在这个过程中，\
    也可以选择让模型根据用户输入的修改意见重新修改文本。
    :param llm_api: 必要参数，实例化后的大模型调用接口
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param text_answer_message: 必要参数，用于表示上层函数创建的一条包含文本内容的message
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :param delete_some_messages: 可选参数，表示在拼接messages时是否删除中间若干条消息，默认为Fasle。
    :param is_task_decomposition: 可选参数，是否是当前执行任务是否是审查任务拆解结果，默认为False。
    :return: message，拼接了最新大模型回答结果的message
    """
   # 从text_answer_message中获取模型回答结果并打印
    answer_content = text_answer_message.content

    print("🤖: Mate Response：\n")
    print(answer_content)

    # 创建指示变量user_input，用于记录用户修改意见，默认为None
    user_input = None

    # 若是开发者模式，或者是增强模式下任务拆解结果，则引导用户对其进行审查
    # 若是开发者模式而非任务拆解
    if not is_task_decomposition and is_developer_mode:
        user_input = input("对话模式：你好，请问是否记录回答结果，记录结果请输入1；\
        对当前结果提出修改意见请输入2；\
        重新进行提问请输入3，\
        直接退出对话请输入4")
        if user_input == '1':
            # 若记录回答结果，则将其添加入msg对象中
            messages.messages_append(text_answer_message)
            print(">>> 本次对话结果已保存")

    # 若是任务拆解
    elif is_task_decomposition:
        user_input = input("【进行任务拆解】请问是否按照该流程执行任务（1），\
        或者对当前执行流程提出修改意见（2），\
        或者重新进行提问（3），\
        或者直接退出对话（4）")
        if user_input == '1':
            # 任务拆解中，如果选择执行该流程
            messages.messages_append(text_answer_message)
            print(">>> 好的，即将逐步执行上述流程")
            messages.messages_append({"role": "user", "content": "非常好，请按照该流程逐步执行。"})
            is_task_decomposition = False
            is_enhanced_mode = False
            messages = get_chat_response(
                llm_api=llm_api,
                messages=messages,
                available_functions=available_functions,
                is_developer_mode=is_developer_mode,
                is_enhanced_mode=is_enhanced_mode,
                delete_some_messages=delete_some_messages,
                is_task_decomposition=is_task_decomposition)


    if user_input is not None:
        if user_input == '1':
            pass
        elif user_input == '2':
            new_user_content = input("好的，输入对模型结果的修改意见：")
            print(">>> 好的，正在进行修改。")
            # 在messages中暂时记录上一轮回答的内容
            messages.messages_append(text_answer_message)
            # 记录用户提出的修改意见
            messages.messages_append({"role": "user", "content": new_user_content})

            # 再次调用主函数进行回答，为了节省token，可以删除用户修改意见和第一版模型回答结果
            # 因此这里可以设置delete_some_messages=2
            # 此外，这里需要设置is_task_decomposition=is_task_decomposition
            # 当需要修改复杂任务拆解结果时，会自动带入is_task_decomposition=True
            messages = get_chat_response(
                llm_api=llm_api,
                messages=messages,
                available_functions=available_functions,
                is_developer_mode=is_developer_mode,
                is_enhanced_mode=is_enhanced_mode,
                delete_some_messages=2,
                is_task_decomposition=is_task_decomposition)

        elif user_input == '3':
            new_user_content = input("好的，请重新提出问题：")
            # 修改问题
            messages.messages[-1]["content"] = new_user_content
            # 再次调用主函数进行回答
            messages = get_chat_response(
                llm_api=llm_api,
                messages=messages,
                available_functions=available_functions,
                is_developer_mode=is_developer_mode,
                is_enhanced_mode=is_enhanced_mode,
                delete_some_messages=delete_some_messages,
                is_task_decomposition=is_task_decomposition)

        else:
            messages.messages_append(text_answer_message)
            print(">>> 好的，已退出当前对话")

    # 若不是开发者模式
    else:
        # 记录返回消息
        messages.messages_append(text_answer_message)

    return messages


def is_code_response_valid(
        llm_api:LlmBox,
        messages:ChatMessages,
        function_call_message:MessageType,
        available_functions=None,
        is_developer_mode=False,
        is_enhanced_mode=False,
        delete_some_messages=False,
        **kwargs
):
    """
    负责完整执行一次外部函数调用的最高层函数，要求输入的msg最后一条消息必须是包含function call的消息。\
    函数的最终任务是将function call的消息中的代码带入外部函数并完成代码运行，并且支持交互式代码编写或自动代码编写运行不同模式。\
    当函数运行得到一条包含外部函数运行结果的function message之后，会继续将其带入check_get_final_function_response函数，\
    用于最终将function message转化为assistant message，并完成本次对话。
    :param llm_api: 必要参数，实例化后的大模型调用接口
    :param model: 必要参数，表示调用的大模型名称
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param function_call_message: 必要参数，用于表示上层函数创建的一条包含function call消息的message
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :param delete_some_messages: 可选参数，表示在拼接messages时是否删除中间若干条消息，默认为Fasle。
    :return: message，拼接了最新大模型回答结果的message
    """

    '''
    TUDO: 有递归调用的风险
    '''
    code_json_str = function_call_message.tool_calls[0].function.arguments

    def display_code():
        '''给用户展示即将运行的代码，如果是开发模式，就让用户看看需不需要修改'''

        code_dict = json.loads(code_json_str)
        print(">>> 即将执行以下代码：")

        if code_dict.get('sql_query'):
            code = code_dict.get('sql_query')
            md_code = f"```sql\n{code}\n```"
        elif code_dict.get('py_code'):
            code = code_dict.get('py_code')
            md_code = f"```python\n{code}\n```"
        else:
            md_code = code_dict

        print(md_code)

    try:
        display_code()
    except Exception as e:
        print(f">>> 代码展示错误:{e}")

        messages = get_chat_response(
            llm_api=llm_api,
            messages=messages,
            available_functions=available_functions,
            is_developer_mode=is_developer_mode,
            is_enhanced_mode=is_enhanced_mode,
            delete_some_messages=delete_some_messages,
        )
        return messages


    # 如果时开发者模式，提示用户对代码进行审然后再运行
    if is_developer_mode:
        user_input = input("如果想直接运行代码，就输入1, 如果想反馈修改意见就让模型对代码进行修改后再运行,输入2。")
        if user_input == "1":
            print("💻：好的，正在运行代码，请稍等...")
        else:
            modify_input = input("好的，请输入修改意见：")
            # 记录模型当前创建的代码和修改意见，等模型获取到意见再生成新代码后，再把这两条删掉
            """
            这里有个bug：就是模型返回tool_calls消息后，后面需要紧跟着一条tool_calls运行后的结果
            这里的解决方法是：不把tool_calls添加进messages中，而是提取出它的内容到messages中，
            变成普通的文本响应，这样后面就不需要跟tool_calls运行的结果
            """
            # messages.messages_append(function_call_message)
            tool_calls_to_text = {'role': 'assistant', 'content': code_json_str}
            fix_suggestion = {'role': 'user', 'content': modify_input}
            messages.messages_append(tool_calls_to_text) # tool_calls变成文本
            messages.messages_append(fix_suggestion)

            # 调用大模型重新返回结果
            messages = get_chat_response(
                llm_api=llm_api,
                messages=messages,
                available_functions=available_functions,
                is_developer_mode=is_developer_mode,
                is_enhanced_mode=is_enhanced_mode,
                delete_some_messages=2
            )
            # print("is_code_response_valid：", messages.messages[-3:])
            return messages

    # 如果是非开发者模式，或者开发者模式下用户不进行代码修改，直接调用运行函数，运行代码获得结果
    function_response_message = function_to_call(
        available_functions=available_functions,
        function_call_message=function_call_message
    )
    print(f"💻: 代码运行结果：{function_response_message}")
    # 将代码运行结果带入到审查函数中
    messages = check_get_final_function_response(
        llm_api=llm_api,
        messages=messages,
        function_call_message=function_call_message,
        function_response_message=function_response_message,
        available_functions=available_functions,
        is_developer_mode=is_developer_mode,
        is_enhanced_mode=is_enhanced_mode,
        delete_some_messages=delete_some_messages
    )
    return messages


def get_chat_response(
        llm_api:LlmBox,
        messages:ChatMessages,
        available_functions=None,
        is_developer_mode=False,
        is_enhanced_mode=False,
        is_task_decomposition=False,
        delete_some_messages=False
):
    '''
    单轮对话任务主函数，负责两种路径的调度：1、文本对话任务；2、function call任务
    负责完整执行一次对话的最高层函数，需要注意的是，一次对话中可能会多次调用大模型，而本函数则是完成一次对话的主函数。
    要求输入的messages中最后一条消息必须是能正常发起对话的消息。
    该函数通过调用get_gpt_response来获取模型输出结果，并且会根据返回结果的不同，例如是文本结果还是代码结果，灵活调用不同函数对模型输出结果进行后处理。
    :param llm_api: 必要参数，实例化后的大模型调用接口
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。
    :param is_task_decomposition: 可选参数，是否是当前执行任务是否是审查任务拆解结果，默认为False。
    :param delete_some_messages: 可选参数，表示在拼接messages时是否删除中间若干条消息，默认为Fasle。这里更多的是在进行返修时，将用户第一次回答、以及用户的返回建议进行删除（此时已经生成返修后的回答，不需要第一次回答和返修建议message）
    :return: 拼接本次问答最终结果的messages
    '''
    # 当围绕复杂任务拆解结果进行修改时，才会出现is_task_decomposition=True的情况
    # 当is_task_decomposition=True时，不再重新创建response_message

    # print("chat_response:")
    # for m in messages.messages[-2:]:
    #     print(m)

    if not is_task_decomposition:
        # 先后去单次大模型调用结果
        response_message = get_deepseek_response(
            llm_api=llm_api,
            messages=messages,
            available_functions=available_functions,
            is_developer_mode=is_developer_mode,
            is_enhanced_mode=is_enhanced_mode,
        )
    # 任务拆解情况：1、is_task_composition=True;2、开启增强模式下的function call调用
    if is_task_decomposition or (is_enhanced_mode and response_message.tool_calls):
        # 将is_task_decomposition修改为True,表示当前执行任务俄日复杂任务拆解，拆解成：第一步xxx，第二步xxx：
        is_task_decomposition = True
        task_decomp_few_shot = add_task_decomposition_prompt(messages=messages)
        print(">>> 正在进行任务分解.....")
        # 更新response_message,其中，更新完的resopnse_message就是任务拆解之后的response
        response_message = get_deepseek_response(
            messages=task_decomp_few_shot,
            available_functions=available_functions,
            is_developer_mode=is_developer_mode,
            is_enhanced_mode=is_enhanced_mode
        )
        if response_message.tool_calls:
            print("当前任务无需拆解，可以直接运行。")

    # 若本次调用是由修改对话需求产生的，则按照参数设置删除原始message中的若干条消息
    # 注意：删除中间若干条消息，必须在创建完新的response_message之后在执行
    if delete_some_messages and isinstance(delete_some_messages, int):
        for i in range(delete_some_messages):
            messages.messages_pop(manual=True, index=-1)

    # 到此为止，产生了一个response_message,接下来根据不同类型，调用不同的路径（文本\code）
    if not response_message.tool_calls:
        # 若是文本响应类任务（包括普通文本响应和和复杂任务拆解审查两种情况，都可以使用相同代码）
        func_mode = is_text_response_valid
    else:
        # 如果是调用function call模式，此时输入的response_message是一个包含SQL或者python代码的JSON对象，输入给代码审查&执行的函数，输出为外部函数运行后的结果
        func_mode = is_code_response_valid

    messages = func_mode(
        llm_api,
        messages,
        response_message,
        available_functions,
        is_developer_mode,
        is_enhanced_mode,
        delete_some_messages,
        is_task_decomposition=is_task_decomposition
    )
    return messages