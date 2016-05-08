from setuptools import setup

APP = ['AnalysisApp.py']
OPTIONS = {
    'iconfile': 'app.icns',
    'plist': {'CFBundleShortVersionString':'0.1.0',
              'CFBundleLocalizations':'en_US.UTF-8',
              'LSEnvironment':{'LANG':'en_US.UTF-8','LC_ALL':'en_US.UTF-8'}}
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
