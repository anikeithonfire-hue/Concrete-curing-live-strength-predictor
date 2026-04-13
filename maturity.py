# maturity method for concrete strength prediction
# based on nurse-saul equation which is a standard
# method used in construction industry worldwide
# basically says : strength depends on temperature X time
# cold weather = slower curing, hot weather = faster curing
# below -10 deg C hydration basically stops completley
 
# nurse saul maturity index formula
# M = sum of (T_concrete - T_datum) * delta_t
# T_datum = -10 deg C (below this no hydration happens)
# delta_t is in hours
# M is in degree-celsius-hours (C.h)
 
# strength prediction using hyperbolic equation
# fc(M) = f28 * ( M / (beta + M) )
# f28   = 28 day design strength in MPa (we use 30 MPa for M30 grade)
# beta  = maturity value at which strength = f28/2
#         for ordinary portland cement beta is around 900 C.h
# this gives us a nice S-curve from 0 to f28
 
T_DATUM   = -10.0    # deg celsius, below this no curing
F28       = 30.0     # design strength MPa (M30 grade concrete)
BETA      = 900.0    # calibration constant for OPC cement