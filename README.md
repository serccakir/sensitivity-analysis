## Sensitivity analysis in multi-criteria evaluation of the suitabilityof urban green spaces for recreational activities


[![DOI](https://zenodo.org/badge/355944806.svg)](https://zenodo.org/badge/latestdoi/355944806)


### Reproduction steps of this study are listed as follows:

1. This study results 3 different outputs as its final results for the sensitivity analysis method. These outputs are shown in the manuscripts as follows:
- **Table 2.** Simulation of criteria weights for the activity *playing Frisbee* within the range of [-100%, +100%]
- **Table 3.** Sensitivity of UGS suitability to the criteria weight simulation
- **Figure 3.** Illustration of UGS suitability in the city of Dresden upon *playing Frisbee* with the base meadow flatness weight (middle), decreased weight by -100% (top), and increased weight by +100% (bottom)

2. To be able to acquire the above mentioned outputs, following data and source code are required:
- ./data/data_frisbee.json 
- ./data/city_border.json
- ./sensitivity_analysis.py
- ./weightSimulation_scoreCalculation.py

Here the **data_frisbee.json** is the main input data including urban green space (UGS) geometries and their associated indicator values for playing Frisbee.    **city_border.json** is including only the geometry for the city of Dresden to visualize the city border in **Figure 3**. 

3. **weightSimulation_scoreCalculation.py** is including 2 functions that simulate the criteria weights for the sensitivity analysis approach and calculate suitability scores for each UGS. **sensitivity_analysis.py** is creating all needed 3 outputs by using those 2 functions from **weightSimulation_scoreCalculation.py**. Table outputs are in the form of .tex file to be used in LaTex and the figure is a .png file.
    
**Please note that we performed all computations in **Windows OS**.

---

Here the main code to be run is **sensitivity_analysis.py**, and the following dependencies are required to be installed in order to perform the sensitivity analysis:

### Software and Main Dependencies:
- Python == 3.7.4
- Pandas
- GeoPandas
- NumPy
- Jenkspy
- Matplotlib
- Contextily
    
**In order to create the same working environment as we have, please follow the below instructions:**

1. As listed above, our code is written in **Python**. We suggest you to install the above-mentioned Python version and create a virtual environment using your                 terminal as follows: <br>
    * `python -m venv my_virtual_env`
2. activate your virtual environment
    * `.\my_virtual_env\Scripts\activate`
3. create a folder called *sensitivity_analysis* and copy all the files from the repository to this folder:
    * `mkdir sensitivity_analysis`
4. navigate your working directory to that folder:
    * `cd sensitivity_analysis`
5. to be able to install some of the main dependencies, you will need to first install the following requirements:
    * `pip install wheel`
    * `pip install pipwin`
6. you are now eligible to install all the requirements:
    * `pipwin install -r requirements1.txt`
    * `pip install -r requirements2.txt`
7. once all the dependencies are installed, please run **sensitivity_analysis.py**:
    * `python sensitivity_analysis.py`
    * above code will produce 3 outputs: *criteria_weight_simulation_table.tex*, *sensitivity_UGS_scores.tex*, and *meadow_flatness_SA.png* 
