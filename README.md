# How to use high-throughput migration calculation machine

###Citation

If you are using the codes in this repo, please consider citing the following work:

Rong, Z., et al., *An efficient algorithm for finding the minimum energy path for cation migration in ionic materials.* The Journal of Chemical Physics, 2016. 145(7): p. 074112.

---

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
1. Prepare an input file in the format like `production/Mg_PF_example.txt`
2. Run script `production/pf_production.py`
3. Set up a crontab job to run script like `production/crontab.qlaunch.sh` regularly at the 
desired frequency at the calculation clusters.

## Deploy ApproxNEB HT calculations
1. Prepare an input file in the format like `production/Mg_approx_neb_example.txt`, first column being the **mp-id**, 
second column being the **pair_index** defined in the database.
2. Set parameters and run script `approx_neb_production.py`
3. Set up a crontab job to run script like `production/crontab.qlaunch.sh` regularly at the 
desired frequency at the calculation clusters.

### Post calculation
After the HT ApproxNEB calculation is finished, do the following steps:
1. Backup the calculation files. (I do it in Vega)
2. Update the calculation file path in the database after files migrations with script like `post_production/db_scripts/update_file_path_vega.py`
3. Update the CONTCARs of each calculated image with script like `post_production/db_scripts/update_contcar.py`

## Results Analysis