from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
            name='tipsip',
            description='SIP stack written in Twisted Python',
            license='MIT',
            url = 'http://github.com/ivaxer/tipsip',
            keywords = "SIP VoIP",

            author='John Khvatov',
            author_email='ivaxer@imarto.net',

            packages = find_packages(),

            test_suite='tipsip.tests',
    )
