#!/usr/bin/env python
""" Plotting utilities for rocks.
"""
import numpy as np
import matplotlib.pyplot as plt

import rocks

# Define colors/markers for all methods in ssodnet
s = {
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
    # -2d on sky
    "OCC": {"color": "brown", "marker": "P"},
    "IM": {"color": "oranged", "marker": "p"},
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
}

ylabels = {"diameter": "Diameter (km)", "mass": "Mass (kg)", "albedo": "Albedo"}


def show_scatter_hist(info, par, figname):

    # translate input
    n = len(info[1])
    x = np.linspace(1, n, n)

    val = info[1].get(par).values
    unc = info[1].get("err_" + par).values
    avg = info[0][0]
    std = info[0][1]

    # Define figure layout
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=(7, 2),
        wspace=0.05,
        left=0.07,
        right=0.97,
        bottom=0.05,
        top=0.87,
    )
    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)

    # the scatter plot:
    # mean and std
    lavg = ax.axhline(avg, label="Average", color=s["avg"]["color"])
    lstd = ax.axhline(
        avg + std,
        label="1$\sigma$ deviation",
        color=s["std"]["color"],
        linestyle="dashed",
    )
    lstd = ax.axhline(avg - std, color=s["std"]["color"], linestyle="dashed")

    # all methods
    for i in np.unique(info[1].method):
        p = np.where(info[1].method == i)
        if True in info[1].selected.values[p]:
            fcol = s[i]["color"]
        else:
            fcol = "none"
        ax.scatter(
            x[p],
            val[p],
            marker=s[i]["marker"],
            s=80,
            label=i,
            facecolors=fcol,
            edgecolors=s[i]["color"],
        )
        ax.errorbar(x[p], val[p], yerr=unc[p], c=s[i]["color"], linestyle="")

    # axes
    ax.set_ylabel(ylabels[par])
    ax.set_xticks(x)

    # Legend
    ax.legend(loc="best", ncol=2)

    # place shortbib on top for quick identification
    axtop = ax.twiny()
    axtop.set_xticks(x)
    axtop.set_xticklabels(info[1].shortbib, rotation=25, ha="left")

    # Histogram
    range = ax.get_ylim()
    nbins = 10
    ax_histy.tick_params(axis="y", labelleft=False)
    sel = np.where(info[1].selected == True)

    na, ba, pa = ax_histy.hist(
        val,
        bins=nbins,
        range=range,
        orientation="horizontal",
        color="grey",
        label="All",
    )
    ns, bs, ps = ax_histy.hist(
        val[sel],
        bins=nbins,
        range=range,
        orientation="horizontal",
        color="gold",
        label="Selected",
    )

    ax_histy.legend(loc="lower right")

    plt.savefig(figname)
    plt.close()


def scatter(self, nbins=10, show=False, savefig=None):
    """Create scatter/histogram figure for float parameters"""

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=(7, 2),
        wspace=0.05,
        left=0.07,
        right=0.97,
        bottom=0.05,
        top=0.87,
    )
    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)

    avg, std = self.weighted_average()
    ax.axhline(avg, label="Average", color=rocks.utils.METHODS["avg"]["color"])
    ax.axhline(
        avg + std,
        label=fr"1$\sigma$ deviation",
        linestyle="dashed",
        color=rocks.utils.METHODS["std"]["color"],
    )
    ax.axhline(avg - std, linestyle="dashed", color=rocks.utils.METHODS["std"]["color"])

    x = np.linspace(1, len(self), len(self))
    for i, m in enumerate(np.unique(self.method)):
        cur = np.where(np.asarray(self.method) == m)
    fcol = "none"
    ax.scatter(
        x[cur],
        np.asarray(self)[cur],
        label=m,
        marker=rocks.utils.METHODS[m]["marker"],
        s=80,
        facecolors=fcol,
        edgecolors=rocks.utils.METHODS[m]["color"],
    )
    ax.errorbar(
        x[cur],
        np.asarray(self)[cur],
        yerr=np.asarray(self.error)[cur],
        c=rocks.utils.METHODS[m]["color"],
        linestyle="",
    )

    ax.set_xticks(x)
    axtop = ax.twiny()
    axtop.set_xticks(x)
    axtop.set_xticklabels(self.shortbib, rotation=25, ha="left")
    ax.set_ylabel(rocks.utils.PLOTTING["LABELS"][self.__name__])
    ax.legend(loc="best", ncol=2)

    range_ = ax.get_ylim()
    ax_histy.tick_params(axis="y", labelleft=False)
    ax_histy.hist(
        self,
        bins=nbins,
        range=range_,
        orientation="horizontal",
        color="grey",
        label="All",
    )
    ax_histy.legend(loc="lower right")

    if savefig is not None:
        fig.savefig(savefig)
    return

    if show:
        plt.show()
    plt.close()
    return

    return fig, ax


def hist(self, nbins=10, show=False, savefig=None):
    """Create histogram figure for float parameters"""

    fig = plt.figure(figsize=(8, 6))
    plt.hist(self, bins=nbins, label="Estimates")
    avg, std = self.weighted_average()
    plt.errorbar(avg, 0.5, xerr=std, label="Average", marker="o")
    plt.legend(loc="upper right")
    plt.xlabel(rocks.utils.PLOTTING["LABELS"][self.__name__])
    plt.ylabel("Distribution")

    if savefig is not None:
        fig.savefig(savefig)
    return

    if show:
        plt.show()
    plt.close()
    return

    return fig
