# How to use high-throughput migration calculation machine

### Setup external computational environment

1. Setup a personal MongoDB database. Update access confidentiality in `settings/db_config.yaml`
2. Install Materials Project [MPWorks](https://github.com/materialsproject/MPWorks) in the computation clusters to be deployed for the HT calculations.
3. Install the following dependency packages locally:
    * [pymatgen](https://github.com/materialsproject/pymatgen)
    * [custodian](https://github.com/materialsproject/custodian)
    * [fireworks](https://github.com/materialsproject/fireworks)

### Deploy PathFinder HT calculations
 