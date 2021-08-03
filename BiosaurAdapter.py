#! /usr/bin/env python3

import argparse 
import logging
import pandas as pd
from pyopenms import *
import time
import os
import biosaur_src.biosaur as bsr

def timing(f):
    """
    Helper function for timing other functions

    Parameters
    ----------
    arg1 : function

    Returns
    -------
    funciton
        new function wrap with timer and logging 
    """
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        logging.info('{:s} function took {:.3f} s'.format(f.__name__, (time2-time1)))
        return ret
    
    return wrap

def process_arg(args):
    """
    Convert namespace args objet to dictionary.

    Helper function. conversion of the args from namespace to dictionary
    allows for easier passing and modification.

    Parameters
    ----------
    args : 
    
        args manespace object from argspars

    Returns
    -------
    dict : 
        dictionary of arguments
    """
    return vars(args)

@timing
def write_feature(args):
    """
    Write feature file

    Read command line arguments and use psims package to format and write mzml

    Parameters
    ----------
    args : args manespace object from argspars

    Returns
    -------
    None
    """
        
    logging.info("Reading features from Biosaur")

    df = pd.read_csv(args["output_file"], sep='\t')

    #Create and Populate FeatureMap

    print([ bytes(args["input"].encode()) ])
    fm = FeatureMap()
    fm.setPrimaryMSRunPath( [ bytes(args["input"].encode()) ] )
    for row in df.itertuples():
        feature = Feature()

        rtStart = row.rtStart*60.0
        rtEnd = row.rtEnd*60.0
        rtApex = row.rtApex*60.0

        hull = ConvexHull2D()
        mzend = row.mz + row.nIsotopes / row.charge 

        hull.addPoint([rtStart,row.mz]) 
        hull.addPoint([rtEnd,row.mz]) 
        hull.addPoint([rtEnd,mzend]) 
        hull.addPoint([rtStart,mzend]) 

        feature.setMZ( float(row.mz ))
        feature.setRT( float(rtApex ) )
        feature.setCharge( int(row.charge) )
        feature.setIntensity( float(row.intensityApex) )
        feature.setOverallQuality( float( row.cos_corr_2 )  )
        feature.setConvexHulls([hull])
        feature.setMetaValue(b"biosaur_massCalib" , float(row.massCalib) )
        feature.setMetaValue(b"biosaur_rtApex" , float(row.rtApex) )
        feature.setMetaValue(b"biosaur_intensityApex" , float(row.intensityApex) )
        feature.setMetaValue(b"biosaur_charge" , float(row.charge) )  
        feature.setMetaValue(b"biosaur_nIsotopes" , float(row.nIsotopes) )    
        feature.setMetaValue(b"biosaur_nScans" , float(row.nScans) )     
        feature.setMetaValue(b"biosaur_cos_corr_1" , float(row.cos_corr_1) )     
        feature.setMetaValue(b"biosaur_cos_corr_2" , float(row.cos_corr_2) )     
        feature.setMetaValue(b"biosaur_diff_for_output" , float(row.diff_for_output) )                              
        feature.setMetaValue(b"biosaur_ion_mobility" , float(row.ion_mobility) )
        feature.setMetaValue(b"biosaur_FAIMS" , float(row.FAIMS) )        

        fm.push_back(feature)
    
    logging.info("writing featureXML: {}".format(args['output']))

    # Write featureXML file
    fm.setUniqueIds()

    FeatureXMLFile().store(args['output'], fm)

    logging.info("writing featureXML: {}".format(args['output']))

def main():
    """
    Main Function

    Parse arguments and start writing

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Argument Parser
    parser = argparse.ArgumentParser(description="tdf2mzml")

    parser.add_argument(
        '-in',
        '--input',
        required=True,
        help='Input File')

    parser.add_argument(
        '-out',
        '--output',
        help='Output File')


    parser.add_argument(
        '-pxfp',
        '--pep_xml_file_path',
        default='0',
        help='Pepxml filepath')

    parser.add_argument(
        '-cm',
        '--correlation_map',
        help='Add correlation map to final table',
        action='store_true')

    parser.add_argument(
        '-nm',
        '--negative_mode',
        help='Add negative mode option',
        action='store_true')

    parser.add_argument(
        '-ac',
        '--mass_accuracy',
        help='Mass accuracy',
        type=float,
        default=8)

    parser.add_argument(
        '-minc',
        '--min_charge',
        help='Minimum charge',
        type=int,
        default=1)

    parser.add_argument(
        '-maxc',
        '--max_charge',
        help='Maximum charge',
        type=int,
        default=6)

    parser.add_argument(
        '-minl',
        '--min_length',
        help='Minimum length',
        type=int,
        default=3)

    parser.add_argument(
        '-minlh',
        '--min_length_hill',
        help='Minimum length for hill',
        type=int,
        default=2)

    parser.add_argument(
        '-mini',
        '--min_intensity',
        type=float,
        help='Minimum intensity',
        default=1)

    parser.add_argument(
        '-hvf',
        '--hill_valley_factor',
        help='Hill Valley Factor',
        type=float,
        default=1.3)

    parser.add_argument(
        '-np',
        '--number_of_processes',
        help='Number of processes',
        default=0)

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debugging output')

    logging.basicConfig(level=logging.INFO)

    args = process_arg(parser.parse_args())

    # Create input arg for Biosaur
    args["input_mzml_path"] = [ args["input"] ]

    # Force the output for Biosaur to conform to the following
    args["output_file"] = "{}.features.tsv".format(os.path.splitext(args["input"])[0])
    
    # If not set, supply a defaute featureXML file name
    if args["output"] == None:
        args["output"] = "{}.featureXML".format(os.path.splitext(args["input"])[0])

    # Fortunately Biosaur uses the logging package
    bsr.bio.process_files(args)

    write_feature(args)
    
if __name__ == "__main__":
    
    main()
