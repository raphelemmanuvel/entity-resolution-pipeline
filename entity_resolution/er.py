import argparse
from pathlib import Path
import pandas as pd
import networkx as nx
from pyvis.network import Network
from itertools import combinations
import numpy as np
import logging

DEFAULT_GH_PAGES_PATH = "docs/index.html"


class EntityResolutionRunner:
    def __init__(self, in_file_path: str, out_plot_path: str) -> None:
        """
        Initialize the EntityResolutionRunner.
        """
        self.in_file_path, self.out_plot_file_name = in_file_path, out_plot_path
        self.out_plot_dir_path = Path(out_plot_path).parent.mkdir(
            parents=True, exist_ok=True
        )
        self.logger = logging.getLogger(__name__)

    def __prepare_data(self) -> None:
        """
        Prepare the data for entity resolution.
        """
        df = pd.read_csv(
            self.in_file_path,
            usecols=[
                "company_id",
                "company_name",
                "owner_name",
                "registered_agent",
                "commercial_registered_agent",
                "principal_address",
            ],
        )
        df["entity_name"] = (
            df[["commercial_registered_agent", "registered_agent", "owner_name"]]
            .bfill(axis=1)
            .iloc[:, 0]
        )
        conditions = [
            df["commercial_registered_agent"].notnull(),
            df["registered_agent"].notnull()
            & df["commercial_registered_agent"].isnull(),
            df["owner_name"].notnull()
            & df["registered_agent"].isnull()
            & df["commercial_registered_agent"].isnull(),
        ]
        df["entity_type"] = np.select(
            conditions,
            ["Commercial Registered Agent", "Registered Agent", "Owner"],
            default=np.nan,
        )
        # Drop rows where entity_name is empty
        self.df_filtered = df.dropna(subset=["entity_name"], how="all")

    def __format_subgraphs(self, G):
        # Get connected components (subgraphs) and assign colors
        components = list(nx.weakly_connected_components(G))
        colors = [
            f"#{i:02x}{(i * 3) % 256:02x}{(i * 5) % 256:02x}"
            for i in range(len(components))
        ]

        # Assign colors to nodes and edges based on connected component
        for i, component in enumerate(components):
            for node in component:
                node_attributes = G.nodes[node]
                self.net.add_node(
                    node,
                    color=colors[i],
                    label=node_attributes.get("label", ""),
                    title=node_attributes.get("title", ""),
                    font={"color": "black", "size": 10},
                )
            for edge in G.edges:
                if edge[0] in component and edge[1] in component:
                    edge_attributes = G.edges[edge]
                    color = (
                        colors[i]
                        if edge_attributes["relationship"] != "same_address"
                        else edge_attributes["color"]
                    )
                    self.net.add_edge(
                        edge[0],
                        edge[1],
                        color=color,
                        label=edge_attributes.get("label", ""),
                    )

    def __create_edge_based_on_address(self, G, company_addresses):
        # Create edges based on address similarity and different company_name
        for (node1, address1), (node2, address2) in combinations(company_addresses, 2):
            if address1 == address2:
                has_edge1_to_2 = G.has_edge(str(node1), str(node2))
                has_edge2_to_1 = G.has_edge(str(node2), str(node1))

                if not (has_edge1_to_2 or has_edge2_to_1):
                    G.add_edge(
                        str(node1),
                        str(node2),
                        relationship="same_address",
                        label="Same Address",
                        color="red",
                    )
        return G

    def __generate_graph(self) -> None:
        """
        Generate a directed graph for entity resolution.
        """
        G = nx.DiGraph()

        # Create a set to store unique addresses for companies
        company_addresses = set()

        for _, row in self.df_filtered.iterrows():
            company_name = row["company_name"]
            company_id = row["company_id"]
            entity_name = row["entity_name"]
            entity_type = row["entity_type"]
            address = row["principal_address"]

            if entity_name:
                G.add_node(
                    str(entity_name),
                    title=f"Name: {entity_name} | Relationship: {entity_type}",
                )

            G.add_node(
                str(company_name),
                label=f"Company: {company_name}",
                title=f"Company ID: {company_id}",
            )

            G.add_edge(
                str(entity_name),
                str(company_name),
                relationship=f"{entity_type}",
                label=f"{entity_type}",
            )

            # Only consider addresses for companies
            if address:
                company_addresses.add((company_name, address))

        G = self.__create_edge_based_on_address(G, company_addresses)

        # Create a pyvis Network from the NetworkX graph
        self.net = Network(notebook=False, directed=True, height="1200px", width="100%")
        # self.net.from_nx(G)
        self.__format_subgraphs(G)

        self.net.set_edge_smooth("dynamic")
        self.net.toggle_physics(True)
        self.net.force_atlas_2based(overlap=1)
        self.net.save_graph(self.out_plot_file_name)
        self.net.save_graph(DEFAULT_GH_PAGES_PATH)  # Save latest copy for GitHub Pages

    def run_er(self) -> None:
        self.logger.info("Running ER pipeline...")
        self.__prepare_data()
        self.__generate_graph()
        self.logger.info("Done...")
