from setuptools import setup, find_packages

setup(
    name='shp2graph',
    version='1.0.0',
    packages=find_packages(),
    package_dir={'shp2graph': 'shp2graph/'},

    install_requires=[
        'geopandas',
        'networkx',
        'rtree',
        'pyyaml'
    ],

    entry_points={
        'console_scrits': [
            'shp2graph=shp2graph.shp2graph:shp2graph'
        ]
    }

    scripts=['final.py', 'config.yaml'],
    data_files=[('', ['config.yaml'])]
)
