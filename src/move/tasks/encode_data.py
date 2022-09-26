__all__ = ["encode_data"]

from pathlib import Path

import numpy as np

from move.conf.schema import DataConfig
from move.core.logging import get_logger
from move.data import io, preprocessing


def encode_data(config: DataConfig):
    """Encodes categorical and continuous datasets specified in configuration.
    Categorical data is one-hot encoded, whereas continuous data is z-score
    normalized.

    Args:
        config: data configuration
    """
    logger = get_logger(__name__)

    # Getting the variables used in the notebook
    raw_data_path = Path(config.raw_data_path)
    raw_data_path.mkdir(exist_ok=True)
    interim_data_path = Path(config.interim_data_path)
    interim_data_path.mkdir(exist_ok=True)

    for dataset_name in config.categorical_names:
        logger.info(f"Encoding '{dataset_name}'")
        names, values = io.read_tsv(raw_data_path / f"{dataset_name}.tsv")
        values = preprocessing.one_hot_encode(values)
        io.dump_feature_names(interim_data_path / f"{dataset_name}.txt", names)
        np.save(interim_data_path / f"{dataset_name}.npy", values)

    for dataset_name in config.continuous_names:
        logger.info(f"Encoding '{dataset_name}'")
        names, values = io.read_tsv(raw_data_path / f"{dataset_name}.tsv")
        values, mask_1d = preprocessing.scale(values)
        names = names[mask_1d]
        logger.debug(f"Columns with zero variance: {np.sum(~mask_1d)}")
        io.dump_feature_names(interim_data_path / f"{dataset_name}.txt", names)
        np.save(interim_data_path / f"{dataset_name}.npy", values)
