from setuptools import setup

setup(
    name="nose-subunit",
    version="0.1",
    description="""\
Output of the nose testing tool result into subunit format.""",
    author="liucougar",
    author_email="liucougar@gmail.com",
    #url="http://maxischenko.in.ua/blog/entries/109/nose-vim-integration",
    #download_url="http://cheeseshop.python.org/pypi/nose_machineout/0.1",
    install_requires = [
        "nose>=0.11",
    ],
    scripts = [],
    license="BSD",
    zip_safe=True,
    py_modules=['sunit'],
    entry_points = {
        'nose.plugins.0.10': ['subunit = sunit:Subunit'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    keywords='test unittest nose',
    test_suite = 'nose.collector'
)
