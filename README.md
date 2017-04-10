# How to use high-throughput migration calculation machine

### Setup external computational environment

1. Setup a personal MongoDB database. Update access confidentiality in `settings/db_config.yaml`
2. Install Materials Project [MPWorks](https://github.com/materialsproject/MPWorks) 
in the computation clusters to be deployed for the HT calculations.
3. Install the following dependency packages locally and familiarize yourself with them:
    * [pymatgen](https://github.com/materialsproject/pymatgen)
    * [custodian](https://github.com/materialsproject/custodian)
    * [fireworks](https://github.com/materialsproject/fireworks)
4. Go through the files under settings and overwrite the variables where necessary
 

### Deploy PathFinder HT calculations
1. Prepare input files in the format like `production/Mg_PF_example.txt`
2. Run script `production/pf_production.py`
3. Set up a crontab job to run script like `production/crontab.qlaunch.sh` regularly at the 
desired frequency at the calculation clusters.


 