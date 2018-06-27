from distutils.core import setup

setup(
    name = 'nfv_tree',
    packages = ['nfv_tree'],
    version = '2.1',
    description = 'versatile I/O operator',
    author = 'Hang Deng',
    author_email = 'hynoor@163.com',
    url = 'https://github.com/hynoor/NFV',
    download_url = 'https://github.com/hynoor/NFV/tree/master/nfv_tree/archive/2.1.tar.gz',
    keywords = ['io_tool', 'test', 'block io', 'nas', 'nfs', 'cifs', 'lock', 'ads', 'io'],
    license = 'MIT',
    include_package_data=True,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)



