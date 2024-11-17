﻿from setuptools import setup, find_packages


setup(
    name='mywxwidgets',  # 你的包名
    version='0.0.1',  # 版本号
    author='Yifan Hong',  # 作者名字
    author_email='1819642087@qq.com',  # 作者邮箱
    description='My wxwidgets for `wxPython`',  # 简短描述
    long_description=open('README.md').read(),  # 长描述，通常是README的内容
    long_description_content_type='text/markdown',  # 长描述的内容类型
    url='https://github.com/H00Hong/my_wxwidgets.git',  # 项目主页
    packages=find_packages(),  # 自动发现所有包和模块
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # 所需的最低Python版本
    install_requires=[  # 依赖列表
        'wxPython',
        'numpy'
    ]
)