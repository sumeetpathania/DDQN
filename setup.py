from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name=NAME,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            'matplotlib',
            'numpy',
            'pandas',
            'torch',
            'tensorboardX']
        )
