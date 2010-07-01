from setuptools import setup

setup(
    name="nose-subunit",
    version="0.1.2",
    description="""Subunit output adapter for nose""",
    long_description="""Change output of the nose testing tool result into subunit format.""",
    author="liucougar",
    author_email="liucougar@gmail.com",
    url="http://www.liucougar.net/blog/nose-subunit",
    download_url="http://pypi.python.org/pypi/nose-subunit/",
    platforms="Independent",
    install_requires = [
        "nose>=0.11",
	#subunit should go here when it's easy installable
    ],
    scripts = [],
    license="BSD",
    zip_safe=False,
    py_modules=['sunit'],
    entry_points = {
        'nose.plugins.0.10': ['subunit = sunit:Subunit'], #, 'warning = warning:Warnings'
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    keywords='test unittest nosetests nose plugin',
    test_suite = 'nose.collector'
)
