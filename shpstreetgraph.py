# ShpStreetGraph
# Copyright (C) [2024] []

# ShpStreetGraph is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# ShpStreetGraph is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import csv
import yaml
import os
import argparse
from datetime import datetime
import geopandas as gpd
import pandas as pd
import networkx as nx


class ShpStreetGraph:
    def __init__(self, config_file, shapefile_path):
        """
        Initialize Shp2Graph class.

        Args:
            config_file (str): Path to the configuration YAML file.
            shapefile_path (str): Path to the shapefile.
        """
        self.config = self.read_yaml(config_file)
        self.data = self.read_shapefile(shapefile_path)
        self.result = None
        self.intersections = None
        self.id_intersections = None
        self.representation = None
        self.graph = None
        self.Id = None

    def read_yaml(self, file_path):
        """
        Read YAML configuration file.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            dict: Parsed YAML contents
        """
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise IOError(f"Error reading the YAML file: {e}")

    def read_shapefile(self, file_path):
        """
        Read shapefile and convert it to GeoDataFrame.

        Args:
            file_path (str): Path to the shapefile.

        Returns:
            GeoDataFrame: Data read from the shapefile.
        """
        self.basename = os.path.basename(file_path)[:-4]
        gdf = gpd.read_file(file_path)
        if self.config['EPSG']:
            return gdf.to_crs(epsg=self.config['EPSG'])
        else:
            return gdf

    def compute_full_names(self):
        """
        Compute full names for streets based on configuration.
        """

        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        self.output_dir = f"output_{self.basename}_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)

        if isinstance(self.config['street_identifier_field'], list):
            fields = self.config['street_identifier_field']
            self.data["Full Name"] = self.data.apply(
                lambda row: ' '.join([str(row[field])
                                     for field in fields if pd.notnull(row[field])])
                or f'Unknown {row.name + 1}', axis=1)

            self.result = self.data.dissolve(by='Full Name').reset_index()
            self.Id = "Full Name"
        else:
            self.Id = self.config['street_identifier_field']
            self.result = self.data.dissolve(by=self.Id).reset_index()

        return self.result

    def find_intersections(self):
        """
        Find intersections between streets.
        """
        if self.config['spatial_operations'] == 'intersection':

            intersections = gpd.sjoin(self.result, self.result, how="inner",
                                      predicate="intersects", lsuffix="left", rsuffix="right")

        elif self.config['spatial_operations'] == 'distance':

            distance = self.config['distance_range']

            self.result['geometry_buffered'] = self.result['geometry'].buffer(
                distance)

            intersections = gpd.sjoin(self.result.set_geometry(
                'geometry_buffered'), self.result, how="inner", predicate="intersects", lsuffix="left", rsuffix="right")

            self.result = self.result.drop('geometry_buffered', axis=1)

        intersections = intersections[intersections.index <
                                      intersections['index_right']]

        self.intersections = sorted(
            list(zip(intersections.index, intersections['index_right'])))

    def create_graph(self):
        """
        Create graph representation of streets and intersections.
        """
        self.graph = nx.Graph()
        self.representation = []

        if self.config['street_representation'] == 'street_name':
            for idx, street in self.result.iterrows():
                self.graph.add_node(street[self.Id])

            for i, j in self.intersections:
                street1, street2 = self.result.iloc[i][self.Id], self.result.iloc[j][self.Id]
                self.graph.add_edge(street1, street2)
                self.representation.append((street1, street2))

        elif self.config['street_representation'] == 'id':
            for idx, street in self.result.iterrows():
                self.graph.add_node(idx)

            for intersection in self.intersections:
                street1, street2 = intersection
                self.graph.add_edge(street1, street2)

            self.representation = self.intersections

        if self.config['street'] == 'edges':
            self.graph = nx.line_graph(self.graph)

    def export_csv(self):
        """
        Export graph data to CSV format.
        """
        if self.config['output_format_adjlist']:
            if self.config['street'] == 'nodes':
                filepath = os.path.join(self.output_dir, "edges.csv")
                with open(filepath, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['id', 'from', 'to'])
                    for idx, intersect in enumerate(self.representation, start=1):
                        csv_writer.writerow([idx] + list(intersect))
                self.result.to_csv(os.path.join(self.output_dir, "nodes.csv"))
                print("Adjacency list exported to edges.csv (CSV format).")

            elif self.config['street'] == 'edges':
                filepath = os.path.join(self.output_dir, "nodes.csv")
                with open(filepath, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['id', 'intersections'])
                    for idx, node in enumerate(sorted(self.graph.nodes()), start=1):
                        csv_writer.writerow([idx, node])
                self.result.to_csv(os.path.join(self.output_dir, "edges.csv"))
                print("Adjacency list exported to nodes.csv (CSV format).")

    def export_graphml(self):
        """
        Export graph to GraphML format.
        """
        if self.config['output_format_graphml']:
            filepath = os.path.join(self.output_dir, "graph.graphml")
            nx.write_graphml(self.graph, filepath)
            print("Graph exported to graph.graphml (GraphML format).")

    def export_pajek(self):
        """
        Export graph to Pajek format.
        """
        if self.config['output_format_pajek']:
            filepath = os.path.join(self.output_dir, "graph.pajek")
            nx.write_pajek(self.graph, filepath)
            print("Graph exported to graph.pajek (Pajek format).")

    def export_graph(self):
        """
        Call export format functions.
        """
        self.export_csv()
        self.export_graphml()
        self.export_pajek()

    def process_graph(self):
        """
        Call graph functions.
        """
        self.create_graph()
        self.export_graph()

    def analyze(self):
        """
        Analyze the shapefile data and export graph representation.
        """
        self.compute_full_names()
        self.find_intersections()
        self.process_graph()


def get_arguments():
    """
    Parse command line arguments.

    Returns:
        Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Convert shp to graphs')
    parser.add_argument('-s', '--shapefile', type=str,
                        required=True, help='Path to shapefile')
    parser.add_argument('-p', '--print_head', action='store_true',
                        help='Print the head of the GeoDataFrame')
    parser.add_argument('-e', '--EPSG', action='store_true',
                        help="Show the CRS (Coordinate Reference System) of your shapefile")

    return parser.parse_args()


def main():
    """
    Main function to execute the conversion process.
    """
    args = get_arguments()
    analyzer = ShpStreetGraph('config.yaml', args.shapefile)

    if args.print_head:
        pd.set_option('display.max_columns', None)
        print(analyzer.data.head(3))
        return

    if args.EPSG:
        print(repr(analyzer.data.crs))
        return

    analyzer.analyze()


if __name__ == "__main__":
    main()
