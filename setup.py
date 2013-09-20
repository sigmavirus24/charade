kw = { 
    'zip_safe' : False,
    'packages' : ['charade'],
}

try:
    from setuptools import setup
    kw['entry_points'] = {
        'console_scripts' : [
            'charade = charade:charade_cli'
        ],
    }
    
except ImportError:
    from distutils.core import setup  # NOQA

    # patch distutils if it can't cope with the "classifiers" or "download_url"
    # keywords (prior to python 2.3.0).
    from distutils.dist import DistributionMetadata
    if not hasattr(DistributionMetadata, 'classifiers'):
        DistributionMetadata.classifiers = None
    if not hasattr(DistributionMetadata, 'download_url'):
        DistributionMetadata.download_url = None

    # When installing the charade script, we want to make it executable on Windows.
    # There are many ways to do this, but this seems to be the best. 'Borrowed'
    # from: http://matthew-brett.github.io/pydagogue/installing_scripts.html
    import os.path

    try:
        from distutils.command.install_scripts import install_scripts

        BAT_FILE_TEMPLATE = r"""@echo off
    set mypath=%~dp0
    set pyscript="%mypath%{FNAME}"
    set /p line1=<%pyscript%
    if "%line1:~0,2%" == "#!" (goto :goodstart)
    echo First line of %pyscript% does not start with "#!"
    exit /b 1
    :goodstart
    set py_exe=%line1:~2%
    call %py_exe% %pyscript% %*
    """
        class WindowsScriptCompat(install_scripts):
            """
            A class that ensures that executable scripts correctly install on
            Windows.
            """
            def run(self):
                install_scripts.run(self) # Ugh, old-style classes.

                if os.name == "nt":
                    for filepath in self.get_outputs():
                        # If we can find an executable in the shebang of a script
                        # file, make a batch file wrapper for it.
                        with open(filepath, 'rt') as f:
                            first_line = f.readline()

                        if not (first_line.startswith('#!') and 
                                'python' in first_line.lower()):
                            continue

                        path, name = os.path.split(filepath)
                        froot, extension = os.path.splitext(name)
                        bat_file = os.path.join(path, froot + '.bat')
                        bat_contents = BAT_FILE_TEMPLATE.replace('{FNAME}', name)

                        if not self.dry_run:
                            with open(bat_file, 'wt') as out:
                                out.write(bat_contents)

                return

        kw["script"] = ['bin/charade']
        cmdclass={'install_scripts': WindowsScriptCompat},

    except ImportError:
        # Uh...let's just hope the user isn't on Windows!
        pass

from charade import __version__

setup(
    name='charade',
    version=__version__,
    description='Universal encoding detector for python 2 and 3',
    long_description='\n\n'.join([open('README.rst').read(),
                                  open('HISTORY.rst').read()]),
    author='Mark Pilgrim',
    author_email='mark@diveintomark.org',
    maintainer='Ian Cordasco',
    maintainer_email='graffatcolmingov@gmail.com',
    url='https://github.com/sigmavirus24/charade',
    license="LGPL",
    keywords=['encoding', 'i18n', 'xml'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public"
        " License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    **kw
)
