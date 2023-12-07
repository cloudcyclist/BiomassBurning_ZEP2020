#reading the trajectory data
def read_traj(filepath, event):
    D=str(filepath)
    ncd = Dataset(D +"BB_" + str(event) + '_gdas_ZEP_500m_460h.nc')

    lat = np.array(ncd["lat"])
    lon = np.array(ncd["lon"])
    alt = np.array(ncd["height"])
    rainfall = np.array(ncd["rainfall"])
    md = np.array(ncd['mixdepth'])
    time = np.array(ncd["time"][:, 0])
    
    return lon, lat, alt, rainfall,md, time


def make_traj_dataset(filepath, event):
    #Reads in a netCDF file and returns the data as a dataset
    lon,lat,alt,rainfall,md,time = read_traj(filepath, event)

    #make a dataset and create a second time variable
    output_ds = xr.Dataset()
    output_ds['starttime'] = xr.DataArray(time, dims=( 'traj'))
    output_ds['lon'] = xr.DataArray(lon, dims=('traj', 'back_time'))
    output_ds['lat'] = xr.DataArray(lat, dims=('traj', 'back_time'))
    output_ds['alt'] = xr.DataArray(alt, dims=('traj', 'back_time'))
    output_ds['md'] = xr.DataArray(md, dims=('traj', 'back_time'))
    output_ds['precip'] = xr.DataArray(rainfall, dims=('traj', 'back_time'))
    
    #make readable date format
    time_corr = []
    for tt in range(len(time[:])):
        time_corr.append(datetime(1600, 1, 1, 0, 0, 0, 0) + timedelta(time[tt]))
    output_ds['time'] = xr.DataArray(time_corr, dims=( 'traj'))

    output_ds = output_ds.assign_coords(traj=output_ds.time)

    return output_ds

def frequency_of_visit(C):
    C = np.array(C)
    mask = np.insert((np.diff(C) - 1).astype(bool), 0, True)
    visits = C[mask].size

    return visits / NUMBER_OF_TRAJECTORIES * 100

def make_monthly_df(df):
    df_monthly = pd.DataFrame(columns=['fires', 'frp_mean', 'frp_25', 'frp_75', 'confidence_mean'])
    df_monthly['fires'] = (df.groupby(df.index.month)['frp'].count())/20
    df_monthly['frp_median'] = df.groupby(df.index.month)['frp'].median()
    df_monthly['frp_25'] = df.groupby(df.index.month)['frp'].quantile(0.25)
    df_monthly['frp_75'] = df.groupby(df.index.month)['frp'].quantile(0.75)
    df_monthly['confidence_mean'] = df.groupby(df.index.month)['confidence'].mean()
    df_monthly['month'] = df_monthly.index

    return df_monthly

def make_2020_df(df):
    df_i = pd.DataFrame(columns=['fires', 'frp'])
    df_i['frp']= df['frp'].resample('M').mean()   
    df_i['fires']= df['frp'].resample('M').count()

    df_2020 = df_i['2020-01-01':'2020-12-31']
    return df_2020

