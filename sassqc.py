import numpy as np
import qc

def qc_tests(df):
    data = df['temperature'].values
    # Location Test
    # Climatology Test
    # Rate of Change Test
    # Time Series Flat Line Test
    # Attenuated Signal Test
    # Range Check
    sensor_span = (-5,30)
    user_span = (8,30)
    qcflagsRange = qc.range_check(data,sensor_span,user_span)
    qc2flags = np.zeros_like(qcflagsRange, dtype='uint8')
    qc2flags[(qcflagsRange > 2)] = 1 # Range
    # Flat Line Check
    low_reps = 2
    high_reps = 5
    eps = 0.0001
    qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
    qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
    # Spike Test
    low_thresh = 2
    high_thresh = 3
    qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
    qc2flags[(qcflagsSpike > 2)] = 3 # Spike
    # Find maximum qc flag
    qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
    # Output flags
    df['temperature_flagPrimary'] = qcflags
    df['temperature_flagSecondary'] = qc2flags

    # Conductivity
    data = df['conductivity'].values
    # Range Check
    sensor_span = (0,9)
    user_span = None
    qcflagsRange = qc.range_check(data,sensor_span,user_span)
    qc2flags = np.zeros_like(qcflagsRange, dtype='uint8')
    qc2flags[(qcflagsRange > 2)] = 1 # Range
    # Flat Line Check
    low_reps = 2
    high_reps = 5
    eps = 0.00005
    qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
    qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
    # Spike Test
    #low_thresh = 2
    #high_thresh = 3
    #qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
    qcflagsSpike = np.zeros_like(qcflagsRange, dtype='uint8')
    #qc2flags[(qcflagsSpike > 2)] = 3 # Spike
    # Find maximum qc flag
    qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
    # Output flags
    df['conductivity_flagPrimary']=qcflags
    df['conductivity_flagSecondary']=qc2flags

    # Pressure
    data = df['pressure'].values
    # Range Check
    user_span = (1,7) # dbar
    sensor_span = (0,20) # dbar
    qcflagsRange = qc.range_check(data,sensor_span,user_span)
    qc2flags = np.zeros_like(qcflagsRange, dtype='uint8')
    qc2flags[(qcflagsRange > 2)] = 1 # Range
    # Flat Line Check
    low_reps = 2
    high_reps = 5
    eps = 0.0005 # Strain gauge 0.004% of full scale range
    qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
    qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
    # Spike Test
    low_thresh = 4 # dbar
    high_thresh = 5 # dbar
    qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
    qc2flags[(qcflagsSpike > 2)] = 3 # Spike
    # Find maximum qc flag
    qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
    # Output flags
    df['pressure_flagPrimary']=qcflags
    df['pressure_flagSecondary']=qc2flags

    # Salinity
    data = df['salinity'].values
    # Range Check
    sensor_span = (2,42) # Practical Salinity Scale of 1978 is valid only in the range of 2 to 42 psu
    user_span = (30,34.5)
    qcflagsRange = qc.range_check(data,sensor_span,user_span)
    qc2flags = np.zeros_like(qcflagsRange, dtype='uint8')
    qc2flags[(qcflagsRange > 2)] = 1 # Range
    # Flat Line Check
    low_reps = 3
    high_reps = 5
    eps = 0.00004 # 0.4ppm in salinity
    qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
    qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
    # Spike Test
    low_thresh = 0.4
    high_thresh = 0.5
    qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
    qc2flags[(qcflagsSpike > 2)] = 3 # Spike
    # Find maximum qc flag
    qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
    # Output flags
    df['salinity_flagPrimary']=qcflags
    df['salinity_flagSecondary']=qc2flags

    # Chlorophyll
    data = df['chlorophyll'].values
    # Range Check
    sensor_span = (0.02,50) # ug/L
    user_span = sensor_span # Needs to
    qcflagsRange = qc.range_check(data,sensor_span,user_span)
    qc2flags = np.zeros_like(qcflagsRange, dtype='uint8')
    qc2flags[(qcflagsRange > 2)] = 1 # Range
    # Flat Line Check
    low_reps = 2
    high_reps = 5
    eps = 0.001 # RMS noise <1mV  0.03 migrograms/L (0.003 raw units)
    qcflagsFlat = qc.flat_line_check(data,low_reps,high_reps,eps)
    qc2flags[(qcflagsFlat > 2)] = 2 # Flat line
    # Spike Test
    low_thresh = 0.8
    high_thresh = 1.0
    qcflagsSpike = qc.spike_check(data,low_thresh,high_thresh)
    qc2flags[(qcflagsSpike > 2)] = 3 # Spike
    # Find maximum qc flag
    qcflags = np.maximum.reduce([qcflagsRange, qcflagsFlat, qcflagsSpike])
    # Output flags
    df['chlorophyll_flagPrimary']=qcflags
    df['chlorophyll_flagSecondary']=qc2flags

    return df
