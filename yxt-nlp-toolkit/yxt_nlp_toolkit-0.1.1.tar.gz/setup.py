from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='yxt_nlp_toolkit',
    version='0.1.1',
    description='common utils for yxt nlp processing',
    long_description=readme(),
    keywords='yunxuetang nlp',
    author='wanglijun',
    author_email='juns1984@qq.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: Linguistic',
    ],
    url='https://github.com/junix/yxt_nlp.git',
    packages=[
        'yxt_nlp',
        'yxt_nlp.common',
        'yxt_nlp.utils',
        'yxt_nlp.utils.jieba_dict',
        'yxt_nlp.embedding',
    ],
    install_requires=[
        # 'gensim==3.4.0',
        'jieba',
    ],
    include_package_data=True,
    zip_safe=False
)
