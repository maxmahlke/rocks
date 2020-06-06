#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 06 June 2020

    Plot utilities

    Part of the rocks CLI suite
'''

import numpy as np
import matplotlib.pyplot as plt


s={'avg':{'color':'black'},
   'std':{'color':'lightgrey'},
  #-Space mission
   'SPACE':{'color':'grey', 'marker':'d'}, 
  #-Thermal models
   'STM':{'color':'grey', 'marker':'d'}, 
   'NEATM':{'color':'darkgrey', 'marker':'o'}, 
   'TPM':{'color':'red', 'marker':'s'}, 
  #-3d shape modeling
   'ADAM':{'color':'red', 'marker':'s'}, 
   'SAGE':{'color':'red', 'marker':'s'}, 
   'KOALA':{'color':'red', 'marker':'s'}, 
   'Radar':{'color':'red', 'marker':'s'}, 
  #-LC with scaling
   'LC+OCC':{'color':'red', 'marker':'s'}, 
   'LC+AO':{'color':'red', 'marker':'s'}, 
   'LC+IM':{'color':'red', 'marker':'s'}, 
   'LC+TPM':{'color':'red', 'marker':'s'}, 
   'LC-TPM':{'color':'red', 'marker':'s'}, 
  #-triaxial ellipsoid
   'TE-IM':{'color':'blue', 'marker':'o'},
  #-2d on sky
   'OCC':{'color':'red', 'marker':'s'}, 
   'IM':{'color':'red', 'marker':'s'}, 
   'IM-PSF':{'color':'red', 'marker':'s'}, 
  #-Mass from binary
   'Bin-IM':{'color':'red', 'marker':'s'}, 
   'Bin-Genoid':{'color':'red', 'marker':'s'}, 
   'Bin-PheMu':{'color':'red', 'marker':'s'}, 
   'Bin-Radar':{'color':'red', 'marker':'s'}, 
  #-Mass from deflection
   'DEFLECT':{'color':'red', 'marker':'s'}, 
   'EPHEM':{'color':'red', 'marker':'s'}, 
  #-Taxonomy
   'Phot':{'color':'red', 'marker':'s'}, 
   'Spec':{'color':'red', 'marker':'s'}, 
   }




def scatter_hist(diams, figname):

    # translate input
    # most likely useless, but it may help making the
    # function "parameter agnostic"
    n=len(diams[1])
    x=np.linspace(1,n,n)

    val=diams[1].diameter.values
    unc=diams[1].err_diameter.values
    avg=diams[0][0]
    std=diams[0][1]

    avg=np.mean(val)
    std=np.std(val)

    # Sort values by year? or let it as in ssodnet?


    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(1, 2, 
                          width_ratios=(7, 2), 
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05)
    ax = fig.add_subplot(gs[0])
    ax_histy = fig.add_subplot(gs[1], sharey=ax)


    # the scatter plot:
    ax.axhline(avg, label='Average',
               color=s['avg']['color'])
    ax.fill_between(x, avg-std,
                    avg+std,
                    label='1$\sigma$ deviation',
                    color=s['std']['color'])

    for i in np.unique(diams[1].method):
        p=np.where(diams[1].method==i)
        ax.scatter(x[p], val[p], 
                   marker=s[i]['marker'], 
                   facecolors='none', edgecolors=s[i]['color'], 
                   s=80, 
                   #color=s[i]['color'], 
                   label=i)

    ax.errorbar(x,val, yerr=unc, 
                linestyle='')
    ax.set_ylabel('Diameter (km)')
    #ax.set_ylim( avg-3*std, avg+3*std ) 
    ax.set_xticks(x)

    # legend for method marker
    ax.legend(loc='best')


    # place shortbib on top for quick identification 
    secax = ax.secondary_xaxis('top')
    secax.set_xticks(x)
    secax.set_xticklabels(diams[1].shortbib) 

 
    # Histogram
    # no labels
    ax_histy.tick_params(axis="y", labelleft=False)
    sel=np.where(diams[1].selected==True)
    print(sel)

    ax_histy.hist(val, orientation='horizontal', label='All')
    ax_histy.hist(val[sel], orientation='horizontal', label='Selected')

    # now determine nice limits by hand:
    #binwidth = 0.25
    #xymax = max(np.max(np.abs(x)), np.max(np.abs(val)))
    #lim = (int(xymax/binwidth) + 1) * binwidth
    #bins = np.arange(-lim, lim + binwidth, binwidth)
    #ax_histy.hist(val, bins=bins, orientation='horizontal')

    plt.savefig(figname)




