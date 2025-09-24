"""
Data Analyst Agent - 智能数据分析助手
"""

from .core import AvailableFunctions, InterProject, DataFlowAgent
from .functions_lib import python_inter, sql_inter, extract_data,fig_inter


__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "AvailableFunctions",
    "InterProject",
    "DataFlowAgent",
]

# 便捷函数
def create_agent():
    """创建数据分析代理"""
    af = AvailableFunctions(
        functions_list=[sql_inter, extract_data, python_inter, fig_inter]
    )
    data_dictionary = open('D:/LZL/workspace/NLP/06agent/ARGC/00Learning/telco_data/telco_data_dictionary.md').read()

    return DataFlowAgent(
        available_functions=af,
        system_content_list=[data_dictionary],
        env_path='.env')
