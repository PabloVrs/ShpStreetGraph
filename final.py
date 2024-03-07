import geopandas as gpd
import pandas as pd
import yaml
import networkx as nx
from itertools import combinations
import csv


class shp2graph:
    def __init__(self, config_file, shapefile_path):
        self.config = self.read_yaml(config_file)
        self.data = self.read_shapefile(shapefile_path)
        self.result = None
        self.intersections = None
        self.graph = None

    def read_yaml(self, file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def read_shapefile(self, file_path):
        gdf = gpd.read_file(file_path)
        return gdf.to_crs(self.config['EPSG'])

    def compute_full_names(self):
        if type(self.config['street_identifier_field']) == list:

            fields = self.config['street_identifier_field']
            full_names = []
            unknown_count = 1

            for index, row in self.data.iterrows():
                valid_values = [str(row[field])
                                for field in fields if pd.notnull(row[field])]

                if not valid_values:
                    full_name = f'Unknown {unknown_count}'
                    unknown_count += 1
                else:
                    full_name = ' '.join(valid_values)

                full_names.append(full_name)

            self.data["Full Name"] = full_names
            self.result = self.data.dissolve(by='Full Name')
            self.result = self.result.reset_index()

            self.Id = "Full Name"

        else:
            self.result = self.data
            self.Id = self.config['street_identifier_field']

    def find_intersections(self):
        intersections = set()
        id_intersections = set()

        for (idx1, street1), (idx2, street2) in combinations(self.result.iterrows(), 2):
            if idx1 < idx2 and street1.geometry.intersects(street2.geometry):
                intersections.add((street1[self.Id], street2[self.Id]))

                id_intersections.add((idx1, idx2))

        self.intersections = list(intersections)
        self.id_intersections = sorted(list(id_intersections))

    def find_interserctions_distance(self):
        intersections = set()
        id_intersections = set()

        for (idx1, street1), (idx2, street2) in combinations(self.result.iterrows(), 2):
            if idx1 < idx2 and street1['geometry'].buffer(self.config['distance_km']).intersects(street2.geometry):
                intersections.add((street1[self.Id], street2[self.Id]))

                id_intersections.add((idx1, idx2))

        self.intersections = list(intersections)
        self.id_intersections = sorted(list(id_intersections)) 

    def create_graph(self):
        self.graph = nx.Graph()

        for idx, street in self.result.iterrows():
                self.graph.add_node(street['Full Name'])

        for intersection in self.intersections:
                street1, street2 = intersection
                self.graph.add_edge(street1, street2)
            
        if self.config['street'] == 'edges':
            self.graph = nx.line_graph(self.graph)
    

    def export_csv(self):
        if self.config['output_format_adjlist']:

            with open('shp2graph_filename_edges.csv', 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['id', 'from', 'to'])

                for idx, intersect in enumerate(self.id_intersections, start=1):
                    csv_writer.writerow([idx] + list(intersect))

            self.result.to_csv("shp2graph_filename_nodes.csv")

            print("Graph exported to shp2graph_filename_nodes.csv (csv format).")

    def export_graphml(self):
        if self.config['output_format_graphml']:
            nx.write_graphml(self.graph, "shp2graph_filename_graph.graphml")
            print("Graph exported to shp2graph_filename_graph.graphml (GraphML format).")

    def export_pajek(self):
        if self.config['output_format_pajek']:
            nx.write_pajek(self.graph, "shp2graph_filename_graph.pajek")
            print("Graph exported to shp2graph_filename_graph.pajek (Pajek format).")

    def export_graph(self):
        self.export_csv()
        self.export_graphml()
        self.export_pajek()

    def analyze(self):
        self.compute_full_names()
        if self.config['spatial_operations'] == 'intersection':
            self.find_intersections()
        elif self.config['spatial_operations'] == 'distance':
            self.find_interserctions_distance()
        self.create_graph()
        self.export_graph()


if __name__ == "__main__":
    analyzer = shp2graph(
        'config.yaml', 'IBGE/mg_faces_de_logradouros_2021/3100203_faces_de_logradouros_2021.shp')
    analyzer.analyze()

