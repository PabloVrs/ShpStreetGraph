# This file is part of ShpStreetGraph.

# ShpStreetGraph is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ShpStreetGraph is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from setuptools import setup, find_packages

setup(
    name='shpstreetgraph',
    version='1.0.0',
    url='https://github.com/PabloVrs/ShpStreetGraph',
    packages=find_packages(),
    package_dir={'shpstreetgraph': 'shpstreetgraph/'},

    install_requires=[
        'geopandas',
        'networkx',
        'rtree',
        'pyyaml'
    ],

    entry_points={
        'console_scripts': [
            'shpstreetgraph=shpstreetgraph.shpstreetgraph:main'
        ]
    },

    scripts=['shpstreetgraph.py'],
    data_files=[('', ['config.yaml'])]
)
