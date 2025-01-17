# FormFiller 表格填充助手

## 项目简介
本项目旨在实现根据当前复制字段自动在剪贴板填充对应文字的功能。通过该项目，可以在填充表格等重复性较高的场景提高操作效率。

## 功能特点
- 功能 1：快速调用数据并在指定位置粘贴
- 功能 2：通过语言模型寻找同义词并匹配字段（仍在开发中）

## 技术栈
- （几乎全部）使用python构建
- GUI框架使用tkinter
- 服务端采用Fastapi和uvicorn
- 由于数据量较小，（目前）仅用CSV或XLSX储存数据

## 使用方法

### 前提条件
- python == 3.12
(理论上3.9以后都可以尝试，3.13会有scipy构建问题)

### 安装步骤
1. 克隆本项目到本地或直接下载ZIP包：

```bash
git clone https://github.com/usernameAlreadyTaken7Times/form_filler
```

2. 进入项目目录：

```bash
cd FormFiller
```

3. (a) 自行构建启动conda或venv虚拟环境,并从requirements.txt安装依赖。

```bash
# venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1 (Windows)
# conda略
```

```bash
pip install -r requirements.txt
```

3. (b) 如果希望使用语言模型，请自行下载Word2Vec格式的中文模型并放到FormFiller/asset/models/目录下。例如[fasttext](lhttps://fasttext.cc/)或[Chinese Word Vectors](https://github.com/Embedding/Chinese-Word-Vectors)，随后运行convert.py脚本转换成bin模式方便程序加载。

```bash
# fasttext中文模型
curl "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.vec.gz"
cd asset/models/
python convert.py
```

4. 运行项目：

```bash
python main.py
```
## 实现原理
- 通过Word2Vec加载语言模型
- 通过keyboard监听Ctrl+C复制键，通过pyperclip读写剪贴板和键值
- 通过fastapi构建语言模型和分割语句的接口，并用uvicorn构建服务


## 操作过程
- 启动程序，根据用户选择是否加载语言模型
- 程序读取数据文件里的信息并创建字典，启动服务
- 当选中屏幕字段并按下Ctrl+C时，程序读取字段并尝试在字典里匹配
- 如果匹配到则直接返回对应的键值；如果未匹配到则
    - 返回'-'（不使用语言模型时）
    - 尝试寻找近义词，近义词匹配则返回对应键值，未匹配则返回'-'（使用语言模型时）
- 关闭服务并卸载语言模型

## 项目结构

```
FormFiller/
├── scripts/ # 源代码文件夹
│   ├── main.py # 主程序脚本
│   └── xxx.py # 其他脚本文件
├── asset/ # 其他资源
│   ├── data/ # 数据文件夹
│   │   ├── csv_database.csv # CSV数据文件
│   │   └── xlsx_database.xlsx # XLSX数据文件
│   ├── models/ # 语言模型文件夹
│   │   ├── models.bin # 语言模型
│   │   └── xxx.xx # 其他语言模型
│   └── test_doc/ # 测试表格
│       └── test_form.docx # 用于测试的示例表格文件
├── readme.md # 本介绍文档
└── requirements.txt # 依赖文件
```

## 贡献指南
如果您【真的】想为本项目贡献代码【请认真三思】，请按照以下步骤操作：
1. Fork 本仓库
2. 创建分支：`git checkout -b feature-branch`
3. 提交代码：`git commit -m "添加了xx功能"`
4. 推送分支：`git push origin feature-branch`
5. 提交 Pull Request

(写得烂成天坑，不会有人愿意改的)