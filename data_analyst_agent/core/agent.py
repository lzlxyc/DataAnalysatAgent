from .project import InterProject
from .messages import ChatMessages
from .functions import AvailableFunctions
from .chat_engine import get_chat_response

from ..api import LlmBox

class DataFlowAgent:
    '''
    数据自动分析agent
    '''
    def __init__(self,
                 model="deepseek-chat",
                 env_path="../../env",
                 system_content_list=[],
                 project=None,
                 messages=None,
                 available_functions=None,
                 is_enhanced_mode=False,
                 is_developer_mode=False):
        """
        初始参数解释：
        api_key：必选参数，表示调用OpenAI模型所必须的字符串密钥，没有默认取值，需要用户提前设置才可使用MateGen；
        model：可选参数，表示当前选择的Chat模型类型，默认为gpt-3.5-turbo，具体当前OpenAI账户可以调用哪些模型，可以参考官网Limit链接：https://platform.openai.com/account/limits ；
        system_content_list：可选参数，表示输入的系统消息或者外部文档，默认为空列表，表示不输入外部文档；
        project：可选参数，表示当前对话所归属的项目名称，需要输入InterProject类对象，用于表示当前对话的本地存储方法，默认为None，表示不进行本地保存；
        messages：可选参数，表示当前对话所继承的Messages，需要是ChatMessages对象、或者是字典所构成的list，默认为None，表示不继承Messages；
        available_functions：可选参数，表示当前对话的外部工具，需要是AvailableFunction对象，默认为None，表示当前对话没有外部函数；
        is_enhanced_mode：可选参数，表示当前对话是否开启增强模式，增强模式下会自动开启复杂任务拆解流程以及深度debug功能，会需要耗费更多的计算时间和金额，不过会换来Agent整体性能提升，默认为False；
        is_developer_mode：可选参数，表示当前对话是否开启开发者模式，在开发者模式下，模型会先和用户确认文本或者代码是否正确，再选择是否进行保存或者执行，对于开发者来说借助开发者模式可以极大程度提升模型可用性，但并不推荐新人使用，默认为False；
        example:
            >>> xxx
            >>> xxx
        """
        self.model:str = model
        self.project:InterProject = project
        self.system_content_list:list = system_content_list

        self.tokens_thr:int = 12000
        self.messages = ChatMessages(
            system_content_list=self.system_content_list,
            tokens_thr=self.tokens_thr,
        )
        if messages:
            self.messages.messages_append(messages)

        self.available_functions:AvailableFunctions = available_functions
        self.is_enhanced_mode:bool = is_enhanced_mode
        self.is_developer_mode:bool = is_developer_mode

        self.llm_api = LlmBox(env_path, self.model)


    def _base_chat(self):
        return get_chat_response(
            llm_api=self.llm_api,
            messages=self.messages,
            available_functions=self.available_functions,
            is_developer_mode=self.is_developer_mode,
            is_enhanced_mode=self.is_enhanced_mode
        )

    def run(self, question=None):
        """
        MateGen类主方法，支持单次对话和多轮对话两种模式，当用户没有输入question时开启多轮对话，反之则开启单轮对话。\
        无论开启单论对话或多轮对话，对话结果将会保存在self.messages中，便于下次调用
        """
        if question is None:
            while True:
                self.messages = self._base_chat()
                user_input = input("🤖: 您还有其他问题吗？(输入Q或q以结束对话): ")

                if user_input in ['q','Q']:
                    break
                else:
                    user_input_msg = {"role": "user", "content": user_input}
                    self.messages.messages_append(user_input_msg)

                print(f'🤔: {user_input}')
        else:
            self.messages.messages_append({"role": "user", "content": question})
            self.messages = self._base_chat()

    def reset(self):
        """
        重置当前的MateGen对象的messages
        """
        self.messages = ChatMessages(
            system_content_list=self.system_content_list
        )

    def upload_messages(self):
       """
       将当前messages上传至project项目中
       """
       if self.project is None:
           print("需要先输入project参数（需要是一个InterProject对象），才可上传messages")
           return None
       else:
           self.project.append_doc_content(
               content=self.messages.history_messages
           )
