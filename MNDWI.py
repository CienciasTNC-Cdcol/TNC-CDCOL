__autor__ = "TNC - Ideam - Miguel Angel Canon Ramos"
__credits__ = ["none"]
__license__ = "Uso Libre"
__version__ = "1.0"
__correo__ = "cienciastnc@gmail.com, miguelca27@gmail.com"
__status__ = "Finalizado"


"""
Algoritmo para la indetificacion de agua, mediante el indice  Modificación Índice de Agua de Diferencia Normalizada (MNDWI)
las entradas corresponden a imagenes satelitales en formato Xarray, este codigo es para uso en la plataforma 
Cubo de datos http://cdcol.ideam.gov.co
"""


# -*- coding: utf-8 -*-



import xarray as xr
import numpy as np
print "Excecuting ndwi v1 "

def isin(element, test_elements, assume_unique=False, invert=False):
    "definiendo la función isin de numpy para la versión anterior a la 1.13, en la que no existe"
    element = np.asarray(element)
    return np.in1d(element, test_elements, assume_unique=assume_unique, invert=invert).reshape(element.shape)



minValid=1
normalized=True
nbar = xarr0
nodata=-9999
bands=["green","swir1"]
medians={}
cvalidValues=set()
if product=="LS7_ETM_LEDAPS" or product=="LS5_TM_LEDAPS":
    validValues=[66,68,130,132]
elif product == "LS8_OLI_LASRC":
    validValues=[322, 386, 834, 898, 1346, 324, 388, 836, 900, 1348]

cloud_mask=isin(nbar["pixel_qa"].values, validValues)


for band in bands:
    datos=np.where(np.logical_and(nbar.data_vars[band]!=nodata,cloud_mask),nbar.data_vars[band], np.nan)
    allNan=~np.isnan(datos)
    if normalized:
        m=np.nanmean(datos.reshape((datos.shape[0],-1)), axis=1)
        st=np.nanstd(datos.reshape((datos.shape[0],-1)), axis=1)
        datos=np.true_divide((datos-m[:,np.newaxis,np.newaxis]), st[:,np.newaxis,np.newaxis])*np.nanmean(st)+np.nanmean(m)
    medians[band]=np.nanmedian(datos,0)
    medians[band][np.sum(allNan,0)<minValid]=np.nan
del datos
period_green = medians["green"]
period_nir = medians["swir1"]
del medians
mask_nan=np.logical_or(np.isnan(period_green), np.isnan(period_nir))
period_ndwi = np.true_divide( np.subtract(period_green,period_nir) , np.add(period_green,period_nir) )
period_ndwi[mask_nan]=np.nan
#Hace un clip para evitar valores extremos.
period_ndwi[period_ndwi>1]=1.0
period_ndwi[period_ndwi<-1]=np.nan
import xarray as xr
ncoords=[]
xdims =[]
xcords={}
for x in nbar.coords:
    if(x!='time'):
        ncoords.append( ( x, nbar.coords[x]) )
        xdims.append(x)
        xcords[x]=nbar.coords[x]
variables ={"ndwi": xr.DataArray(period_ndwi, dims=xdims,coords=ncoords)}
output=xr.Dataset(variables, attrs={'crs':nbar.crs})
for x in output.coords:
    output.coords[x].attrs["units"]=nbar.coords[x].units
