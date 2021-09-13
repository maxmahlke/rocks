#!/usr/bin/env python
""" Plotting utilities for rocks."""
import matplotlib.pyplot as plt
import pandas as pd

import rocks


def plot(catalogue, parameter, nbins=10, show=True, save_to=""):
    """Create a scatter/histogram figure for asteroid parameters in datacloud
    catalogues.

    Parameters
    ==========
    catalogue : rocks.datacloud.Catalog
        A datacloud catalogue ingested in Rock instance.
    parameter : str
        The parameter name, referring to a column in the datacloud catalogue.
    nbins : int
        Number of bins in histogram. Default is 10
    show : bool
        Show plot. Default is False.
    save_to : str
        Save figure to path. Default is no saving.

    Returns
    =======
    matplotlib.figures.Figure instance, matplotib.axes.Axis instance
    """

    # Look up the correct parameter name
    parameter = PLOTTING["PARAMETERS"][parameter]

    # Reduce the catalogue to the valid entries
    _catalogue = catalogue.loc[
        (catalogue[parameter] != 0) & (~pd.isna(catalogue[parameter]))
    ].copy()

    # Classic diamalbedo if-clause
    if parameter in ["albedo", "diameter"]:
        _catalogue.loc[:, "preferred"] = _catalogue.loc[:, f"preferred_{parameter}"]

    # Reset the catalogue index for easier plotting
    _catalogue = _catalogue.reset_index()

    # ------
    # Define figure layout
    fig, (ax_scatter, ax_hist) = plt.subplots(
        ncols=2,
        figsize=(12, 8),
        sharey=True,
        gridspec_kw={"width_ratios": [7, 2], "wspace": 0.01},
        constrained_layout=True,
    )

    # ------
    # Create the scatter plot

    # Add the observations, coded per method
    for method in set(_catalogue.method):

        # Observations acquired with this method
        obs_method = _catalogue[
            [entry.method == method for _, entry in _catalogue.iterrows()]
        ]

        if obs_method.empty:
            continue

        facecolors = [
            PLOTTING[method]["color"] if preferred else "none"
            for preferred in obs_method["preferred"]
        ]

        ax_scatter.scatter(
            obs_method.index,
            obs_method[parameter],
            marker=PLOTTING[method]["marker"],
            edgecolors=PLOTTING[method]["color"],
            facecolors=facecolors,
            s=80,
            label=method,
        )
        ax_scatter.errorbar(
            obs_method.index,
            obs_method[parameter],
            yerr=obs_method[f"err_{parameter}"],
            color=PLOTTING[method]["color"],
            linestyle="",
        )
    # Add weighted average and error
    avg, err_avg = rocks.utils.weighted_average(_catalogue, parameter)

    ax_scatter.axhline(avg, color=PLOTTING["avg"]["color"], label="Average")
    ax_scatter.axhline(
        avg + err_avg,
        ls="dashed",
        color=PLOTTING["std"]["color"],
        label="1$\sigma$ deviation",
    )
    ax_scatter.axhline(avg - err_avg, ls="dashed", color=PLOTTING["std"]["color"])

    # Axes setup
    ax_scatter.set(
        ylabel=PLOTTING["LABELS"][parameter], xlim=(-0.5, len(_catalogue) - 0.5)
    )
    ax_scatter.set_xticks(_catalogue.index)
    ax_scatter.legend(loc="best", ncol=2, title=f"{avg:.4} +- {err_avg:.4}")

    # ------
    # Place shortbib on top for quick identification
    ax_top = ax_scatter.twiny()
    ax_top.set_xticks(_catalogue.index)
    ax_top.set_xticklabels(_catalogue.shortbib, rotation=25, ha="left")

    # ------
    # Histogram plot

    # Add two histograms: all observations and preferred observations
    ax_hist.hist(
        [entry[parameter] for _, entry in _catalogue.iterrows() if entry["preferred"]],
        bins=nbins,
        range=ax_scatter.get_ylim(),
        orientation="horizontal",
        color="gold",
        label="Preferred",
        histtype="step",
    )
    y, _, _ = ax_hist.hist(
        _catalogue[parameter],
        bins=nbins,
        range=ax_scatter.get_ylim(),
        orientation="horizontal",
        color="grey",
        label="All",
        histtype="step",
        ls="--",
    )

    # Axes setup
    ax_hist.set(xlim=(0, max(y) + 1))
    ax_hist.legend(loc="lower right")
    ax_hist.tick_params(axis="y", labelleft=False)

    if show:
        plt.show()

    if save_to:
        plt.savefig(save_to)


# Define colors/markers for all methods in ssodnet
PLOTTING = {
    "avg": {"color": "black"},
    "std": {"color": "darkgrey"},
    # -Space mission
    "SPACE": {"color": "gold", "marker": "X"},
    # -3d shape modeling
    "ADAM": {"color": "navy", "marker": "v"},
    "SAGE": {"color": "mediumblue", "marker": "^"},
    "KOALA": {"color": "slateblue", "marker": "<"},
    "Radar": {"color": "cornflowerblue", "marker": ">"},
    # -LC with scaling
    "LC+OCC": {"color": "lightgreen", "marker": "v"},
    "LC+AO": {"color": "forestgreen", "marker": "^"},  # deprecated =LC+IM
    "LC+IM": {"color": "forestgreen", "marker": "^"},
    "LC+TPM": {"color": "darkgreen", "marker": "<"},
    "LC-TPM": {"color": "green", "marker": ">"},
    # -Thermal models
    "STM": {"color": "grey", "marker": "D"},
    "NEATM": {"color": "grey", "marker": "o"},
    "TPM": {"color": "darkgrey", "marker": "s"},
    # -triaxial ellipsoid
    "TE-IM": {"color": "blue", "marker": "o"},
    "TE-Occ": {"color": "darkblue", "marker": "o"},
    # -2d on sky
    "OCC": {"color": "brown", "marker": "P"},
    "IM": {"color": "orange", "marker": "p"},
    "IM-PSF": {"color": "tomato", "marker": "H"},
    # -Mass from binary
    "Bin-IM": {"color": "navy", "marker": "v"},
    "Bin-Genoid": {"color": "mediumblue", "marker": "^"},
    "Bin-PheMu": {"color": "slateblue", "marker": "<"},
    "Bin-Radar": {"color": "cornflowerblue", "marker": ">"},
    # -Mass from deflection
    "DEFLECT": {"color": "brown", "marker": "D"},
    "EPHEM": {"color": "red", "marker": "o"},
    # -Taxonomy
    "Phot": {"color": "red", "marker": "s"},
    "Spec": {"color": "red", "marker": "s"},
    # More setup
    "LABELS": {
        "diameter": "Diameter (km)",
        "mass": "Mass (kg)",
        "albedo": "Albedo",
    },
    "PARAMETERS": {
        "albedos": "albedo",
        "albedo": "albedo",
        "diameters": "diameter",
        "diameter": "diameter",
        "masses": "mass",
        "mass": "mass",
    },
}
