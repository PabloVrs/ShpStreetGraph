# Shp2Graph: Convert Shapefiles to Graph Representations

Shp2Graph is a Python tool designed to convert shapefiles into graph representations. This tool uses the `geopandas` library for handling shapefiles, `networkx` for graph representation, and `rtree` for spatial indexing. It allows for various graph export formats such as CSV, GraphML, and Pajek.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration File](#configuration-file)
- [Example](#example)
- [License](#license)

## Installation

To use Shp2Graph, you need to have Python 3.x installed. You can install the required dependencies using pip:

```bash
pip install geopandas pandas pyyaml networkx rtree
```

## Usage

The main script can be run from the command line. It requires a path to a shapefile and a configuration file.

### Command Line Arguments
- `-s, --shapefile`: Path to the shapefile (required).
- `-p, --print_head`: Print the head of the GeoDataFrame and exit.

### Configuration File

Shp2Graph requires a YAML configuration file to specify various parameters for processing the shapefile. Below is an example configuration file (`config.yaml`):

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

If how the street names are represented in the shapefile is not known, you can print the head of the geodataframe:
```bash
shp2graph -s path/to/your/shapefile.shp -p
```
## Example
1. Create a configuration file `config.yaml` with your desired settings.
2. Run the script with your shapefile.
```bash
shp2graph -s path/to/your/shapefile.shp
```
3. The script will process the shapefile and output the results in the specified formats.


