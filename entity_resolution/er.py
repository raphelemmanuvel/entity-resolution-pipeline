import argparse
from pathlib import Path
import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import logging


class EntityResolutionRunner:
    def __init__(self, in_file_path: str, out_plot_path: str) -> None:
        """
        Initialize the EntityResolutionRunner.
        """
        self.in_file_path, self.out_plot_file_name = in_file_path, out_plot_path
        self.out_plot_dir_path = Path(out_plot_path).parent.mkdir(
            parents=True, exist_ok=True
        )
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def __prepare_data(self) -> None:
        """
        Prepare the data for entity resolution.
        """
        df = pd.read_csv(self.in_file_path)
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

    def __generate_graph(self) -> None:
        """
        Generate a directed graph for entity resolution.
        """
        G = nx.DiGraph()

        for _, row in self.df_filtered.iterrows():
            company_name = row["company_name"]
            company_id = row["company_id"]
            entity_name = row["entity_name"]
            entity_type = row["entity_type"]

            if entity_name:
                G.add_node(
                    str(entity_name),
                    node_type="entity",
                    label=f"Name: {entity_name}",
                    title=f"Relationship: {entity_type}",
                )

            G.add_node(
                str(company_name),
                node_type="company",
                label=f"Company: {company_name}",
                title=f"Company ID: {company_id}",
            )
            G.add_edge(
                str(entity_name),
                str(company_name),
                relationship=f"{entity_type}",
                label=f"{entity_type}",
            )

        # Create a pyvis Network from the NetworkX graph
        self.net = Network(notebook=False, directed=True, height="1200px", width="100%")
        self.net.from_nx(G)
        self.net.set_edge_smooth("dynamic")
        self.net.toggle_physics(True)
        self.net.force_atlas_2based(overlap=1)
        self.net.save_graph(self.out_plot_file_name)

    def run_er(self) -> None:
        self.logger.info("Running ER pipeline...")
        self.__prepare_data()
        self.__generate_graph()
        self.logger.info("Done...")


def main():
    parser = argparse.ArgumentParser(description="Entity Resolution Runner..")
    parser.add_argument("input_file", help="Path to the input CSV file..")
    parser.add_argument("output_plot", help="Path to save the output plot..")
    args = parser.parse_args()
    EntityResolutionRunner(args.input_file, args.output_plot).run_er()


if __name__ == "__main__":
    main()
