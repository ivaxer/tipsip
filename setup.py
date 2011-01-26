from setuptools import setup

if __name__ == '__main__':
    setup(
            name='tipsip',
            description='SIP stack on Python',
            license='MIT',
            url = 'http://github.com/ivaxer/tipsip',
            keywords = "SIP VoIP",

            author='John Khvatov',
            author_email='ivaxer@imarto.net',

            test_suite='tipsip.tests',
    )
