import geopandas as gpd
import pandas as pd
import yaml
import networkx as nx
import csv
from datetime import datetime
import os
import argparse
from rtree import index
import multiprocessing


class Shp2Graph:
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
        return gdf.to_crs(self.config['EPSG'])

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
            self.result = self.data
            self.Id = self.config['street_identifier_field']

        return self.result

    def get_IDX(self):
        """
        Create and return an R-tree spatial index for the streets.

        Returns:
            rtree.index.Index: R-tree index.
        """
        IDX = index.Index()
        for idx_, street_ in self.result.iterrows():
            IDX.insert(idx_, street_.geometry.bounds)
        return IDX

    def find_intersections(self, args):
        """
        Find intersections between streets.

        Args:
            args (tuple): Tuple containing index chunk, return dictionary, and process ID.
        """
        idx_chunk, return_dict, process_id = args
        local_intersections = []
        IDX = self.get_IDX()

        for i in idx_chunk:
            street = self.result.iloc[i]
            bounds = street.geometry.bounds
            possibles_idx = list(IDX.intersection(bounds))

            for possible_idx in possibles_idx:
                if i < possible_idx:
                    possible_street = self.result.iloc[possible_idx]
                    if street.geometry.intersects(possible_street.geometry):
                        local_intersections.append((i, possible_idx))

        return_dict[process_id] = local_intersections

    def find_intersections_distance(self, args):
        """
        Find intersections within a specified buffer distance.

        Args:
            args (tuple): Tuple containing index chunk, return dictionary, and process ID.
        """
        idx_chunk, return_dict, process_id = args
        local_intersections = []
        IDX = self.get_IDX()
        distance = self.config['distance_km']

        for i in idx_chunk:
            street = self.result.iloc[i]
            buffered_geometry = street.geometry.buffer(distance)
            possibles_idx = list(IDX.intersection(buffered_geometry.bounds))

            for possible_idx in possibles_idx:
                if i < possible_idx:
                    possible_street = self.result.iloc[possible_idx]
                    if possible_street.geometry.intersects(buffered_geometry):
                        local_intersections.append((i, possible_idx))

        return_dict[process_id] = local_intersections

    def create_graph(self, id_intersections):
        """
        Create graph representation of streets and intersections.

        Args:
            id_intersections (list): List of intersecting street indices.
        """
        self.graph = nx.Graph()
        self.id_intersections = id_intersections
        self.representation = []

        if self.config['street_representation'] == 'street_name':
            for idx, street in self.result.iterrows():
                self.graph.add_node(street[self.Id])

            for i, j in self.id_intersections:
                street1, street2 = self.result.iloc[i][self.Id], self.result.iloc[j][self.Id]
                self.graph.add_edge(street1, street2)
                self.representation.append((street1, street2))

        elif self.config['street_representation'] == 'id':
            for idx, street in self.result.iterrows():
                self.graph.add_node(idx)

            for intersection in self.id_intersections:
                street1, street2 = intersection
                self.graph.add_edge(street1, street2)

            self.representation = self.id_intersections

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
                print(f"Adjacency list exported to edges.csv (CSV format).")

            elif self.config['street'] == 'edges':
                filepath = os.path.join(self.output_dir, "nodes.csv")
                with open(filepath, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['id', 'intersections'])
                    for idx, node in enumerate(sorted(self.graph.nodes()), start=1):
                        csv_writer.writerow([idx, node])
                self.result.to_csv(os.path.join(self.output_dir, "edges.csv"))
                print(f"Adjacency list exported to nodes.csv (CSV format).")

    def export_graphml(self):
        """
        Export graph to GraphML format.
        """
        if self.config['output_format_graphml']:
            filepath = os.path.join(self.output_dir, "graph.graphml")
            nx.write_graphml(self.graph, filepath)
            print(f"Graph exported to graph.graphml (GraphML format).")

    def export_pajek(self):
        """
        Export graph to Pajek format.
        """
        if self.config['output_format_pajek']:
            filepath = os.path.join(self.output_dir, "graph.pajek")
            nx.write_pajek(self.graph, filepath)
            print(f"Graph exported to graph.pajek (Pajek format).")

    def export_graph(self):
        """
        Call export format functions.
        """
        self.export_csv()
        self.export_graphml()
        self.export_pajek()

    def process_graph(self, id_intersections):
        """
        Call graph functions.
        """
        self.create_graph(id_intersections)
        self.export_graph()


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
    return parser.parse_args()


def main():
    """
    Main function to execute the conversion process.
    """
    args = get_arguments()
    analyzer = Shp2Graph('config.yaml', args.shapefile)

    if args.print_head:
        pd.set_option('display.max_columns', None)
        print(analyzer.data.head(3))
        return

    result = analyzer.compute_full_names()
    idxi = result.index

    num_processes = analyzer.config['num_processes']
    chunk_size = len(idxi) // num_processes
    idx_chunks = [idxi[i:i + chunk_size]
                  for i in range(0, len(idxi), chunk_size)]

    with multiprocessing.Manager() as manager:
        Intersections = manager.dict()
        args = [(chunk, Intersections, i)
                for i, chunk in enumerate(idx_chunks)]

        with multiprocessing.Pool(processes=num_processes) as pool:
            if analyzer.config["spatial_operations"] == 'intersection':
                pool.map(analyzer.find_intersections, args)
            elif analyzer.config["spatial_operations"] == 'distance':
                pool.map(analyzer.find_intersections_distance, args)

        id_intersections = [inter for inter in Intersections.values()
                            for inter in inter]
        id_intersections = sorted(id_intersections)

    analyzer.process_graph(id_intersections)


if __name__ == "__main__":
    main()
