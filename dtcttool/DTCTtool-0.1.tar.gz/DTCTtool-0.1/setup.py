import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
  
setuptools.setup(  
      name='DTCTtool',   #名称  
      version='0.1',  #版本  
      description="This is a database comparison tool that ignores data structures and database types", #描述   
      author='ZhangShaoNan',  #作者  
      author_email='758896823@qq.com', #作者邮箱  
      url='https://github.com/1fengchen1', #作者链接  
      packages=setuptools.find_packages(),
	  classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
      install_requires=[      #需求的第三方模块  
        'xlwt ',
		'xlrd',
		'xlutils',
      ],  
      entry_points={  
        'console_scripts':[     #如果你想要以Linux命令的形式使用  
            'bword = bword.bword:main'      
        ]  
      },  
)  