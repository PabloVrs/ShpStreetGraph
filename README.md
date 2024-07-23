# ShpStreetGraph: Spatial Relations of Streets to Graph Representations

ShpStreetGraph is a Python tool designed to convert shapefiles into graph representations. This tool uses the `geopandas` library for handling shapefiles, `networkx` for graph representation, and `rtree` for spatial indexing. It allows for various graph export formats such as CSV, GraphML, and Pajek.

## Table of Contents

- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Command Line Arguments](#command-line-arguments)
  - [Configuration File](#configuration-file)
- [Example](#example)
- [License](#license)

## Getting Started

You can set up this program in two different ways:

### Option 1: Installing via deb package

1. Download the .deb package from the releases section:

  ```bash
  wget https://github.com/PabloVrs/ShpStreetGraph/blob/main/shpstreetgraph_1.0.0.deb
  ```
2. Install the package using dpkg:

  ```bash
  sudo dpkg -i shpstreetgraph_1.0.0.deb
  ```
3. The program will be ready to use.

### Option 2: Packaging the files.

1. Install `stdeb` package:
   
  ```bash
  pip install stdeb
  ```
 
2. Download the setup.py and the shpstreetgraph.py files.
  ```bash
  wget https://github.com/PabloVrs/ShpStreetGraph/blob/main/setup.py
  wget https://github.com/PabloVrs/ShpStreetGraph/blob/main/shpstreetgraph.py
  ```

3. Package the files.
  ```bash
  python3 setup.py --command-packages=stdeb.command bdist_deb
  ```

4. Install the package using dpkg:
   
  ```bash
  sudo dpkg -i shpstreetgraph_1.0.0.deb
  ```
 
### Choose the setup option that best suits your preferences and needs.

## Usage

The main script can be run from the command line. It requires a path to a shapefile and a configuration file.

### Command Line Arguments
- `-s`, `--shapefile`: Path to the shapefile (required).
- `-p`, `--print_head`: Print the head of the GeoDataFrame and exit.
- `-h`, `--help`: Show the list of options.

### Configuration File

ShpStreetGraph requires a YAML configuration file to specify various parameters for processing the shapefile. Below is an example configuration file (`config.yaml`):

```yaml
street: nodes #nodes or edges
spatial_operations: intersection #intersection or distance
distance_km: 0 #distance in km
output_format_adjlist: True 
output_format_graphml: True
output_format_pajek: True

street_representation: id #id or street_name

street_identifier_field:
  - Field1
  - Field2
  - Field3

EPSG: '32723' #Latin America

num_processes: 1
```
#### Configuration Parameters
- `street`: Whether streets are represented as nodes or edges.

- `spatial_operations`: Type of spatial operation (intersection or distance).

- `distance_km`: Buffer distance in kilometers for spatial operations.
  
- `output_format_adjlist`: Whether to export the adjacency list in CSV format.
- `output_format_graphml`: Whether to export the graph in GraphML format.
- `output_format_pajek`: Whether to export the graph in Pajek format.

- `street_representation`: How streets are represented in the graph (street_name or id).

- `street_identifier_field`: List of fields or unique field to identify streets.
  ```
  If street_identifier_field is a list:    |    If is a unique field:
  street_identifier_field:                 |    street_identifier_field: Field                
    - Field1                               |
    - Field2                               |
    - Fieldn                               |
  ```
- `EPSG`: The EPSG code for the coordinate reference system to use.

- `num_processes`: Number of processes to use for multiprocessing.

When you are not certain about the street names, you can print the head of the geodataframe:
```bash
shpstreetgraph -s path/to/your/shapefile.shp -p
```
## Example
1. Create a configuration file `config.yaml` with your desired settings.
2. Run the script with your shapefile.

  ```bash
  shpstreetgraph -s path/to/your/shapefile.shp
  ```
3. The script will process the shapefile and output the results in the specified formats.

#### Using a shp from a small part of Price, a city from Utah for different config settings:


| `spatial_operations: intersection` | `spatial_operations: distance` |
|:--------------------------------:|:--------------------------------:|
| ![example](https://github.com/PabloVrs/ShpStreetGraph/blob/main/images/example.png) | ![buffered_example](https://github.com/PabloVrs/ShpStreetGraph/blob/main/images/buffered_example.png) |
| **CSV Output 1** | **CSV Output 2** |

| id | from | to | id | from | to |
|---|---|---|---|---|---|
| 7 | East Ninth North | North 100 East | 7 | East Ninth North | North 100 East |
| 8 | East Ninth North | North East First Street | 8 | East Ninth North | North East First Street |
| 14 | Hillcrest Drive | North 100 East | 14 | Hillcrest Drive | North 100 East |
| 18 | North 100 East | Covecrest Street | 18 | North 100 East | North East First Street |
| | | | 19 | North 100 East | Covecrest Street |

Note that using `distance`, with the specific radius, the streets "North 100 East" and "North East First Street" intersect!

The example files are available at [examples](https://github.com/PabloVrs/ShpStreetGraph/tree/main/examples).

## License

This project is licensed under the GNU General Public License version 3 (GPLv3) - see the [LICENSE](COPYING.txt) file for details.
