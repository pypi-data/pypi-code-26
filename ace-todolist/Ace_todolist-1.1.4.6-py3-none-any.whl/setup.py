from setuptools import setup, find_packages

setup(
    name             = 'Ace_todolist',
    version          = '1.1.3.4',
    description      = 'todolist by Ace',
    license          = 'MIT',
    author           = 'Ace',
    author_email     = 'qmffhrmdyd123@naver.com',
    url              = 'https://github.com/taaeyoon/Ace_todolist',
    download_url     = 'https://github.com/taaeyoon/Ace_todolist/archive/master.zip',
    packages         = find_packages(exclude = ['coding_convention', 'repository_rules']),
    keywords         = 'todolist by Ace',
    python_requires  = '>=3.6',
    entry_points     = {
                        'console_scripts': [
                        'Ace_todolist = Ace_todolist.__main__:run_program',
                        ],
                        },
    zip_safe = False,
    classifiers      = [
        'Programming Language :: Python :: 3.6'
    ]
)
