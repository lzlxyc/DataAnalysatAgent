import os
import json
import shutil


def create_or_get_folder(folder_name):
    """
    创建或获取文件夹ID，本地存储时获取文件夹路径
    return: folder_id
    """
    # 若存储本地，则获取文件夹路径，且同时命名为folder_id
    folder_path = os.path.join('./', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def create_or_get_doc(folder_id, doc_name):
    """
    创建或获取文件ID，本地存储时获取文件路径
    return: document_id
    """
    file_path = os.path.join(folder_id, f'{doc_name}.md')
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')  # 创建一个带有标题的空Markdown文件
    document_id = file_path

    return document_id

def get_file_content(file_id):
    """
    获取文档的具体内容，需要区分是读取谷歌云文档还是读取本地文档
    """
    with open(file_id, 'r', encoding='utf-8') as file:
        decoded_content = file.read()

    return decoded_content

def append_content_in_doc(doc_id, dict_list):
    """
    创建文档，或为指定的文档增加内容，需要区分是否是云文档
    """
    if isinstance(dict_list, dict):
        # 将字典列表转换为JSON字符串
        json_string = json.dumps(dict_list, indent=4, ensure_ascii=False)
    elif isinstance(dict_list, str):
        json_string = dict_list
    else:
        json_string = str(dict_list)

    print(">>> 数据持久化保存：", doc_id)
    with open(doc_id, 'a', encoding='utf-8') as file:
        file.write(json_string)  # 追加JSON字符串

def clear_content_in_doc(doc_id):
    """
    清空指定文档的全部内容，需要区分是否是云文档
    """
    with open(doc_id, 'w') as file:
        pass  # 清空文件内容

def list_files_in_folder(folder_id):
    """
    列举当前文件夹的全部文件，需要区分是读取谷歌云盘文件夹还是本地文件夹
    """
    return [f for f in os.listdir(folder_id) if os.path.isfile(os.path.join(folder_id, f))]

def rename_doc_in_drive(doc_id, new_name):
    """
    修改指定的文档名称，需要区分是云文件还是本地文件
    return: update_name
    """
    # 分解原始路径以获取目录和扩展名
    directory, old_file_name = os.path.split(doc_id)
    extension = os.path.splitext(old_file_name)[1]

    # 用新名称和原始扩展名组合新路径
    new_file_name = new_name + extension
    new_file_path = os.path.join(directory, new_file_name)

    # 重命名文件
    os.rename(doc_id, new_file_path)

    update_name=new_name

    return update_name

def delete_all_files_in_folder(folder_id):
    """
    删除某文件夹内全部文件，需要区分谷歌云文件夹还是本地文件夹
    """
    for filename in os.listdir(folder_id):
        file_path = os.path.join(folder_id, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'>>> Failed to delete {file_path}. Reason: {e}')

class InterProject:
    """
    项目类：项目是每个分析任务的基础对象，换而言之，每个分析任务应该都是“挂靠”在某个项目中。\
    每个代码解释器必须说明所属项目，若无所属项目，则在代码解释器运行时会自动创建一个项目。\
    需要注意的是，项目不仅起到了说明和标注当前分析任务的作用，更关键的是，项目提供了每个分析任务的“长期记忆”，\
    即每个项目都有对应的谷歌云盘和谷歌云文档，用于保存在分析和建模工作过程中多轮对话内容，\
    此外，也可以选择借助本地文档进行存储。
    """
    def __init__(self,
                 project_name,
                 doc_name,
                 folder_id=None,
                 doc_id=None,
                 doc_content=None
    ):
        self.project_name = project_name
        self.doc_name = doc_name

        if folder_id is None:
            folder_id = create_or_get_folder(project_name)
        self.folder_id = folder_id

        if doc_id is None:
            doc_id = create_or_get_doc(project_name, doc_name)
        self.doc_id = doc_id

        self.doc_content = doc_content
        if doc_content is not None:
            append_content_in_doc(self.doc_id, self.doc_content)

        self.doc_list = list_files_in_folder(self.folder_id)

    def get_doc_content(self):
        """
        根据项目某文件的文件ID，获取对应的文件内容
        """
        self.doc_content = get_file_content(self.doc_id)

        return self.doc_content

    def append_doc_content(self, content=None):
        """
        根据项目某文件的文件ID，追加文件内容
        """
        if content is None:
            content = self.get_doc_content()

        append_content_in_doc(self.doc_id, content)

    def clear_doc_content(self):
        """
        清空某文件内的全部内容
        """
        clear_content_in_doc(self.doc_id)

    def delete_all_files(self):
        """
        删除当前项目文件夹内的全部文件
        """
        delete_all_files_in_folder(self.folder_id)

    def update_doc_list(self):
        """
        更新当前项目文件夹内的全部文件名称
        """
        self.doc_list = list_files_in_folder(self.folder_id)

    def rename_doc(self, new_name):
        """
        修改当前文件名称
        """
        self.doc_name = rename_doc_in_drive(self.doc_id, new_name)