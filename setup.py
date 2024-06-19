# This file is part of ShpStreetGraph.

# ShpStreetGraph is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    
# ShpStreetGraph is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

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
