from setuptools import setup

setup(
    name="nose-subunit",
    version="0.1",
    description="""
Output of the nose testing tool result into subunit format.""",
    author="liucougar",
    author_email="liucougar@gmail.com",
    url="http://www.liucougar.net/blog/",
    #download_url="",
    install_requires = [
        "nose>=0.11",
    ],
    scripts = [],
    license="BSD",
    zip_safe=False,
    py_modules=['sunit'],
    entry_points = {
        'nose.plugins.0.10': ['subunit = sunit:Subunit'], #, 'warning = warning:Warnings'
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
