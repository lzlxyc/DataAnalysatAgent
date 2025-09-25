

def python_inter(py_code, g:dict='globals()'):
    """
    专门用于执行非绘图类python代码，并获取最终查询或处理结果。若是设计绘图操作的Python代码，则需要调用fig_inter函数来执行。
    :param py_code: 字符串形式的Python代码，用于执行对telco_db数据库中各张数据表进行操作
    :param g: g，字符串形式变量，表示环境变量，无需设置，保持默认参数即可
    :return：代码运行的最终结果
    """

    global_vars_before = set(g.keys())
    try:
        exec(py_code, g)
    except Exception as e:
        return f"代码执行时报错{e}"
    global_vars_after = set(g.keys())
    new_vars = global_vars_after - global_vars_before
    # 若存在新变量
    if new_vars:
        result = {var: g[var] for var in new_vars}
        return str(result)
    # 若不存在新变量，即有可能是代码是表达式，也有可能代码对相同变量重复赋值
    else:
        try:
            # 尝试如果是表达式，则返回表达式运行结果
            return str(eval(py_code, g))
        # 若报错，则先测试是否是对相同变量重复赋值
        except Exception as e:
            try:
                exec(py_code, g)
                return "已经顺利执行代码"
            except Exception as e:
                pass
            # 若不是重复赋值，则报错
            return f"代码执行时报错{e}"


def fig_inter(py_code, fname, g='globals()'):
    """
    用于执行一段包含可视化绘图的Python代码，并最终获取一个图片类型对象
    :param py_code: 字符串形式的Python代码，用于根据需求进行绘图，代码中必须包含Figure对象创建过程
    :param fname: py_code代码中创建的Figure变量名，以字符串形式表示。
    :param g: g，字符串形式变量，表示环境变量，无需设置，保持默认参数即可
    :return：代码运行的最终结果
    """
    import matplotlib
    # 保存当前的后端
    current_backend = matplotlib.get_backend()

    # 设置为Agg后端
    matplotlib.use('notebook')
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    # 创建一个字典，用于存储本地变量
    local_vars = {"plt": plt, "pd": pd, "sns": sns}

    try:
        exec(py_code, g, local_vars)
        return "成功执行完代码。"
    except Exception as e:
        return f"代码执行时报错{e}"

    # 回复默认后端
    # matplotlib.use(current_backend)

    # 根据图片名称，获取图片对象
    # fig = local_vars[fname]
    # return "成功上传图片。"

    # 上传图片
    # res = "无法上传图片至谷歌云盘，请检查谷歌云盘文件夹ID，并检查当前网络情况"
    #
    # print(f'>>> {res}')
    # return res