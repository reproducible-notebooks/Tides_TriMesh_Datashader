
# coding: utf-8

# ## ADCIRC TriMesh data with Datashader
# 
# [Datashader](http://datashader.org) support for irregular triangular meshes allows large ADCIRC datasets to be rendered onscreen efficiently. This notebook shows an example of rendering the depth or M2 Amplitude from the [EC2015 tidal database](https://doi.org/10.3390/jmse4040072).  Make possible by the [EarthSim Project](https://pyviz.github.io/EarthSim/).
# 
# After the map load (takes a while):
# * click one of the zoom tools and zoom into the coast, like New York area
# * try picking M2 Amplitude or other tidal constituent from the dropdown list

# In[1]:


import datashader as ds
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews.operation.datashader import datashade, rasterize
import geoviews as gv
import palettable
import ipywidgets as ipyw
from gridgeo.ugrid import ugrid
from IPython.display import display
import netCDF4
hv.extension("bokeh")


# In[2]:


import time
import _thread
nseconds = 40
progress = ipyw.IntProgress(value=0, max=nseconds)
def update_process():
    for i in range(nseconds):
        progress.value = i
        time.sleep(1)
_thread.start_new_thread(update_process, ())


# In[3]:


def gen_trimesh(value):
    if value == 'M2 Elevation Amplitude':
        z = nc['Amp'][0,:]   
    elif value == 'S2 Elevation Amplitude':
        z = nc['Amp'][1,:]   
    elif value == 'N2 Elevation Amplitude':
        z = nc['Amp'][2,:]        
    elif value == 'O1 Elevation Amplitude':
        z = nc['Amp'][3,:]    
    elif value == 'K1 Elevation Amplitude':
        z = nc['Amp'][4,:]    
    else:
        z = -nc['depth'][:]

    v = np.vstack((u['nodes']['x'], u['nodes']['y'], z)).T
    verts = pd.DataFrame(v, columns=['x','y','z'])
    points = gv.operation.project_points(gv.Points(verts, vdims=['z']))
    label = '{} (m)'.format(value)
    return hv.TriMesh((tris, points), label=label)


# In[4]:


value_stream = hv.streams.Stream.define('Value', value='Depth')()

vars = ['Depth','M2 Elevation Amplitude',
        'S2 Elevation Amplitude','N2 Elevation Amplitude',
        'O1 Elevation Amplitude','K1 Elevation Amplitude']
dpdown = ipyw.Dropdown(options=vars, value=vars[0])

def on_change(change):
   if change['type'] == 'change' and change['name'] == 'value':
       value_stream.event(value=dpdown.value) 



# In[5]:


display(progress)


# In[6]:


# EC2015 data in netCDF form, accessed via OPeNDAP. 
# Here we use a UGRID-ized version of http://tds.renci.org:8080/thredds/dodsC/DataLayers/Tides/ec2015_tidaldb/f53.nc.html
url='http://gamone.whoi.edu/thredds/dodsC/usgs/vault0/models/tides/ec2015/f53.ncml'
nc = netCDF4.Dataset(url)
# Use gridgeo to get mesh from UGRID compliant dataset
u = ugrid(nc)
tris = pd.DataFrame(u['faces'].astype('int'), columns=['v0','v1','v2'])


# In[7]:


dpdown.observe(on_change)


# In[8]:


tiles = gv.WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg')
dynamic_trimesh = hv.DynamicMap(gen_trimesh, streams=[value_stream])
plot = tiles * rasterize(dynamic_trimesh, aggregator=ds.mean('z'), precompute=True) 


# In[9]:


get_ipython().run_line_magic('opts', "Image [colorbar=True clipping_colors={'NaN': (0, 0, 0, 0)}] (cmap=palettable.cubehelix.perceptual_rainbow_16.mpl_colormap)")
get_ipython().run_line_magic('opts', 'WMTS [width=700 height=400]')
plot


# In[10]:


display(dpdown)


# In[11]:


progress.close()

