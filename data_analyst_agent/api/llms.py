import os
import openai
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from dotenv import load_dotenv

MessageDict = dict
MessageType = ChatCompletionMessage


class LlmBox:
    '''
    提供大模型调用服务
    1、默认使用deepseek-chat模型
    2、需要在根目录下配置好.env文件
    '''
    def __init__(self, env_path='../../.env', model_name="deepseek-chat"):
        api_key, api_url = self.init(env_path)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=api_url,
        )
        self.model_name = model_name

        print(f"▌ Model set to {self.model_name}")

    def init(self, env_path:str) -> tuple[str, str]:
        print(f"[1] load env from {env_path}...")
        assert os.path.exists(env_path)

        from dotenv import load_dotenv
        load_dotenv(env_path)
        api_key:str = os.getenv("DS_API_KEY")
        api_url:str = os.getenv("DS_API_URL")
        print(f"[2] set api_key: {api_key}...")
        print(f"[3] set api_url: {api_url}...")

        return api_key, api_url



    def build_messages(self, prompt:str, system_pt=None) -> MessageDict:
        messages = []
        if system_pt is not None:
            messages.append({"role": "system", "content": system_pt})

        messages.append({"role": "user", "content": prompt})

        return messages


    def chat(self, prompt='你好。',
             system_pt=None,
             messages=None,
             tools=None,
             tool_choice='auto') -> MessageType:
        '''基础的大模型问答接口，可以传入提示词，也可以直接传入message
        :param prompt: 提示词
        :param system_pt: 系统提示词
        :param messages: 传入的message
        :param tools: function calls工具
        :param tool_choice: 是否调用外部工具
        :return: 返回大模型输出的message
        '''
        if messages is None:
            messages = self.build_messages(prompt, system_pt)

        if tools is None:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
        return response.choices[0].message


if __name__ == '__main__':
    llmbox = LlmBox()
    llmbox.chat()