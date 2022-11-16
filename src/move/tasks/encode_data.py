__all__ = ["encode_data"]

from pathlib import Path

import numpy as np

from move.conf.schema import DataConfig
from move.core.logging import get_logger
from move.data import io, preprocessing
from move.visualization.dataset_distributions import plot_value_distributions


def encode_data(config: DataConfig):
    """Encodes categorical and continuous datasets specified in configuration.
    Categorical data is one-hot encoded, whereas continuous data is z-score
    normalized.

    Args:
        config: data configuration
    """
    logger = get_logger(__name__)
    logger.info("Beginning task: encode data")

    raw_data_path = Path(config.raw_data_path)
    raw_data_path.mkdir(exist_ok=True)
    interim_data_path = Path(config.interim_data_path)
    interim_data_path.mkdir(exist_ok=True)
    output_path = Path(config.processed_data_path) / "encoded_datasets"
    output_path.mkdir(exist_ok=True, parents=True)

    sample_names = io.read_names(raw_data_path / f"{config.sample_names}.txt")

    mappings = {}
    for dataset_name in config.categorical_names:
        logger.info(f"Encoding '{dataset_name}'")
        filepath = raw_data_path / f"{dataset_name}.tsv"
        names, values = io.read_tsv(filepath, sample_names)
        values, mapping = preprocessing.one_hot_encode(values)
        mappings[dataset_name] = mapping
        io.dump_names(interim_data_path / f"{dataset_name}.txt", names)
        np.save(interim_data_path / f"{dataset_name}.npy", values)
    io.dump_mappings(interim_data_path / "mappings.json", mappings)

    for dataset_name in config.continuous_names:
        logger.info(f"Encoding '{dataset_name}'")
        filepath = raw_data_path / f"{dataset_name}.tsv"
        names, values = io.read_tsv(filepath, sample_names)

        # Plotting the value distribution for all continuous datasets before preprocessing:
        fig = plot_value_distributions(values)
        fig_path = str(output_path / "Value_distribution_{}_unprocessed.png".format(dataset_name))
        fig.savefig(fig_path)

        values, mask_1d = preprocessing.scale(values)
        names = names[mask_1d]
        logger.debug(f"Columns with zero variance: {np.sum(~mask_1d)}")
        io.dump_names(interim_data_path / f"{dataset_name}.txt", names)
        np.save(interim_data_path / f"{dataset_name}.npy", values)

        # Plotting the value distribution for all continuous datasets:
        fig = plot_value_distributions(values)
        fig_path = str(output_path / "Value_distribution_{}.png".format(dataset_name))
        fig.savefig(fig_path)