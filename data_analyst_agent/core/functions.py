import json
import inspect
import numpy as np
import pandas as pd



def auto_functions(functions_list:list):
    """
    Chat模型的functions参数编写函数
    :param functions_list: 包含一个或者多个函数对象的列表；
    :return：满足Chat模型functions参数要求的functions对象
    """
    default_tools = {
'sql_inter': {'function': {'description': '用于执行一段SQL代码，并最终获取SQL代码执行结果，核心功能是将输入的SQL代码传输至MySQL环境中进行运行，最终返回SQL代码运行结果。本函数是借助pymysql来连接MySQL数据库',
                            'name': 'sql_inter',
                            'parameters': {'properties': {'g': {'description': '环境变量，无需设置，保持默认参数即可',
                                                                'type': 'string'},
                                                          'sql_query': {'description': '用于执行对MySQL中telco_db数据库中各张表进行查询，并获得各表中的各类相关信息',
                                                                        'type': 'string'}},
                                           'required': ['sql_query'],
                                           'type': 'object'}},
               'type': 'function'},
'extract_data': {'function': {'description': '借助pymysql将MySQL中的某张表读取并保存到本地Python环境中',
                               'name': 'extract_data',
                               'parameters': {'properties': {'df_name': {'description': '将MySQL数据库中提取的表格进行本地保存时的变量名，以字符串形式表示。',
                                                                         'type': 'string'},
                                                             'g': {'description': '字符串形式变量，表示环境变量，无需设置，保持默认参数即可',
                                                                   'type': 'string'},
                                                             'sql_query': {'description': '字符串形式的SQL查询语句，用于提取MySQL中的某张表。',
                                                                           'type': 'string'}},
                                              'required': ['sql_query',
                                                           'df_name'],
                                              'type': 'object'}},
                  'type': 'function'},
'python_inter': {'function': {'description': '专门用于执行非绘图类python代码，并获取最终查询或处理结果。若是设计绘图操作的Python代码，则需要调用fig_inter函数来执行。',
                               'name': 'python_inter',
                               'parameters': {'properties': {'g': {'description': '环境变量，无需设置，保持默认参数即可',
                                                                   'type': 'string'},
                                                             'py_code': {'description': '用于执行对telco_db数据库中各张数据表进行操作的Python代码',
                                                                         'type': 'string'}},
                                              'required': ['py_code'],
                                              'type': 'object'}},
                  'type': 'function'},
'fig_inter': {'function': {'description': '用于执行一段包含可视化绘图的Python代码，并最终获取一个图片类型对象',
                            'name': 'fig_inter',
                            'parameters': {'properties': {'fname': {'description': '代码中创建的Figure变量名',
                                                                    'type': 'string'},
                                                          'g': {'description': '环境变量，无需设置，保持默认参数即可',
                                                                'type': 'string'},
                                                          'py_code': {'description': '代码中必须包含Figure对象创建过程',
                                                                      'type': 'string'}},
                                           'required': ['py_code', 'fname'],
                                           'type': 'object'}},
               'type': 'function'},
    }
    def functions_generate(functions_list):
        # 创建空列表，用于保存每个函数的描述字典
        functions = []

        def chen_ming_algorithm(data):
            """
            陈明算法函数，该函数定义了一种特殊的数据集计算过程
            :param data: 必要参数，表示带入计算的数据表，用字符串进行表示
            :return：陈明函数计算后的结果，返回结果为表示为JSON格式的Dataframe类型对象
            """
            df_new = pd.read_json(data)
            res = np.sum(df_new, axis=1) - 1
            return res.to_json(orient='records')

        chen_ming_function_description = inspect.getdoc(chen_ming_algorithm)

        chen_ming_function_name = chen_ming_algorithm.__name__

        chen_ming_function = {"name": "chen_ming_algorithm",
                              "description": "用于执行陈明算法的函数，定义了一种特殊的数据集计算过程",
                              "parameters": {"type": "object",
                                             "properties": {"data": {"type": "string",
                                                                     "description": "执行陈明算法的数据集"},
                                                           },
                                             "required": ["data"],
                                            },
                             }


        # 对每个外部函数进行循环
        for function in functions_list:
            function_name = function.__name__
            if function_name in default_tools:
                functions.append(default_tools[function_name])
                continue
            # 读取函数对象的函数说明
            function_description = inspect.getdoc(function)
            # 读取函数的函数名字符串
            user_message1 = '以下是某的函数说明：%s。' % chen_ming_function_description +\
                            '根据这个函数的函数说明，请帮我创建一个function对象，用于描述这个函数的基本情况。这个function对象是一个JSON格式的字典，\
                            这个字典有如下5点要求：\
                            1.字典总共有三个键值对；\
                            2.第一个键值对的Key是字符串name，value是该函数的名字：%s，也是字符串；\
                            3.第二个键值对的Key是字符串description，value是该函数的函数的功能说明，也是字符串；\
                            4.第三个键值对的Key是字符串parameters，value是一个JSON Schema对象，用于说明该函数的参数输入规范。\
                            5.输出结果必须是一个JSON格式的字典，只输出这个字典即可，前后不需要任何前后修饰或说明的语句' % chen_ming_function_name


            assistant_message1 = json.dumps(chen_ming_function)

            user_prompt = '现在有另一个函数，函数名为：%s；函数说明为：%s；\
                          请帮我仿造类似的格式为当前函数创建一个function对象。' % (function_name, function_description)

            '''TUDO:用llm_api注入的方式'''
            response = client.chat.completions.create(
                              model=model_name,
                              messages=[
                                {"role": "user", "name":"example_user", "content": user_message1},
                                {"role": "assistant", "name":"example_assistant", "content": assistant_message1},
                                {"role": "user", "name":"example_user", "content": user_prompt}]
                            )
            one_function = {
                'type': 'function',
                'function': json.loads(response.choices[0].message.content)
            }
            functions.append(one_function)
        return functions

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            functions = functions_generate(functions_list)
            break  # 如果代码成功执行，跳出循环
        except Exception as e:
            attempts += 1  # 增加尝试次数
            print(">>> 发生错误：", e)
            print(">>> 由于模型limit rate导致报错，即将暂停1分钟，1分钟后重新尝试调用模型")
            if attempts == max_attempts:
                print(">>> 已达到最大尝试次数，程序终止。")
                raise  # 重新引发最后一个异常
            else:
                print(">>> 正在重新运行...")
    return functions


class AvailableFunctions:
    """
    外部函数类，主要负责承接外部函数调用时相关功能支持。类属性包括外部函数列表、外部函数参数说明列表、以及调用方式说明三项。
    """
    def __init__(self, functions_list=[], functions=[], function_call="auto"):
        self.functions_list = functions_list
        self.functions = functions
        self.functions_dic = None
        self.function_call = None
        # 当外部函数列表不为空、且外部函数参数解释为空时，调用auto_functions创建外部函数解释列表
        if functions_list != []:
            self.functions_dic = {func.__name__: func for func in functions_list}
            self.function_call = function_call
            if functions == []:
                self.functions = auto_functions(functions_list)

    # 增加外部函数方法，并且同时可以更换外部函数调用规则
    def add_function(self, new_function, function_description=None, function_call_update=None):
        self.functions_list.append(new_function)
        self.functions_dic[new_function.__name__] = new_function
        if function_description == None:
            new_function_description = auto_functions([new_function])
            self.functions.append(new_function_description)
        else:
            self.functions.append(function_description)
        if function_call_update != None:
            self.function_call = function_call_update