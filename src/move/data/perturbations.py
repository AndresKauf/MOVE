__all__ = ["perturb_data"]

from typing import cast

import numpy as np
import torch
from torch.utils.data import DataLoader

from move.data.dataloaders import MOVEDataset, make_dataloader
from move.utils.model_utils import get_start_end_positions


def perturb_data(
    cat_list: list[np.ndarray],
    con_list: list[np.ndarray],
    cat_dataset_names: list[str],
    target_dataset_name: str,
    target_value: np.ndarray,
) -> list[DataLoader]:
    """Add perturbations to training data. For each feature in the target
    categorical dataset change its value to target

    Args:
        cat_list: List of categorical datasets
        con_list: List of continuous datasets
        cat_dataset_names: List of categorical dataset names
        target_dataset_name: Target categorical dataset to perturb
        target_value: Target value

    Returns:
        List of dataloaders, containing all perturbed datasets and the original
        dataset in the last position
    """
    target_idx = cat_dataset_names.index(target_dataset_name)
    target_shape = cat_list[target_idx].shape
    num_samples = cat_list[target_idx].shape[0]
    _, baseline_dataloader = make_dataloader(
        cat_list, con_list, shuffle=False, batch_size=num_samples
    )
    baseline_dataset = cast(MOVEDataset, baseline_dataloader.dataset)
    start, end = get_start_end_positions(
        cat_list, cat_dataset_names, target_dataset_name
    )
    assert baseline_dataset.cat_all is not None
    cat_all = baseline_dataset.cat_all
    num_features = target_shape[1]

    dataloaders = []
    for i in range(num_features):
        perturbed_cat = cat_all.clone()
        target_dataset = perturbed_cat[:, start:end].view(*target_shape)
        target_dataset[:, i, :] = torch.FloatTensor(target_value)
        perturbed_dataset = MOVEDataset(
            perturbed_cat,
            baseline_dataset.con_all,
            baseline_dataset.con_shapes,
            baseline_dataset.cat_shapes,
        )
        perturbed_dataloader = DataLoader(
            perturbed_dataset, shuffle=False, batch_size=num_samples
        )
        dataloaders.append(perturbed_dataloader)
    dataloaders.append(baseline_dataloader)
    return dataloaders
