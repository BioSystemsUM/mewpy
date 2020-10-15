## Evaluation Functions

All evaluation functions/optimization objectives are defined in `mewpy.optimization.evaluation` module.



**Biomass-Product Coupled Yield** (BPCY):

The maximization of the Biomass-Product Coupled Yield is one of the most commonly used objectives in Computational Strain Optimization. 
$$
BPCY = Product \times Growth
$$

```python
from mewpy.optimization.evaluation import BPCY
fevaluation = BPCY(biomass_reaction_id,product_reaction_id)
```

By default, MEWPy computes reaction yields using *pFBA*. This may thought be altered by defining an alternative phenotype simulation method, such as *lMOMA*.



```python
fevaluation = BPCY(biomass_reaction_id,product_reaction_id,method ='lMOMA')
```

Also, the BPCY computation may account for a carbon source or substrate consumption:
$$
BPCY = \frac{Product \times Growth}{Substrate}
$$

```python
from mewpy.optimization.evaluation import BPCY
fevaluation = BPCY(<biomass_reaction_id>,<product_reaction_id>,\
                   uptake=<substrate_reaction_id>)
```



**Weight Yield** (WYIELD):

BPCY, on its own, has some limitations. Although the BPCY score of a mutated solution may be high, the flux value of the target reaction may be unstable with the max biomass. To guide the EA to more robust solutions, MEWpy also includes a weight yield objective, that encompasses the target product flux variability, constrained to a minimal growth and introduced metabolic modifications.
$$
WYIELD = \alpha \times \text{FVA}_{max}(Product)+(1-\alpha)\times \text{FVA}_{min}(Product),\;  \alpha \in [0;1]
$$

```python
from mewpy.optimization.evaluation import WYIELD
fevaluation = WYIELD(<biomass_reaction_id>,<product_reaction_id>)
```

The trade-off parameter  is by default set to 0.3. However it may be changed by adding a new setting the class instantiation. For example,  `alpha=0.5`. 

```python
fevaluation = WYIELD(<biomass_reaction_id>,<product_reaction_id>,alpha=0.5)
```

The minimum growth yield may be explicitly defined, `min_biomass_value=<some_value>`, or as a percentage of the wild type biomass, `min_biomass_per=0.1`, that is 10%.



**BPCY with FVA**

MEWpy also includes an objective function that combines BPCY and WYIELD, whose formulation is:

$$
BPCY\_FVA=\frac{Product \times Growth }{Substrate}\times \left( 1 -\log\frac{\text{FVA}_{max}-\text{FVA}_{min}}{\text{FVA}_{max}+\text{FVA}_{min}}\right)
$$

```python
from mewpy.optimization.evaluation import BPCY_FVA
fevaluation = BPCY_FVA(<biomass_reaction_id>,<product_reaction_id>,uptake=<substrate_reaction_id>)
```

As in BPCY, the substrate is optional and fluxes may be obtained using different phenotype simulation methods.

This objective function is based on a  proposal from "*OptRAM*: *In-silico* strain design via integrative regulatory-metabolic network modeling".



**Product Yield**

The most straight forward objective function is the product yield, where the goal is to maximize the production of a target product. In the MEWpy implementation, this objective function may consider a minimum biomass production explicitly defined or a percentage of the wild type growth. This objective function also may consider distinct phenotype simulation methods. Also, this same objective function may be used for the minimization of a targeted reaction flux by changing the optimization sense, that is, by setting the argument  `maximize=False`.

```python
from mewpy.optimization.evaluation import TargetFlux
fevaluation = TargetFlux(<product_reaction_id>)
```

 

**Minimum number of modifications**

Although problems definition allows for setting a maximum number of modifications, and solutions from the final population may be automatically simplified to remove unnecessary modifications, the minimization of the number of perturbations can be set as an additional optimization objective.  



```python
from mewpy.optimization.evaluation import MinCandSize
fevaluation =  MinCandSize()

```





**Combining two or more objectives**

The previously defined objective functions may be combined into a linear aggregated weighed sum and used in single objective optimization algorithms, such as Genetic Algorithm or Simulated Annealing. 
$$
f_{agg}=\sum_{i=1}^n w_i \times f_i=w_1\times f_1+w_2\times f_2 + ... +w_n \times f_n
$$
Though the sum of all weights should be equal to 1, this is not imposed as weights may also be used to introduce a normalization for each function. When not provided, the aggregated function assigns a same weight to all functions w=1/n.

```python
from mewpy.optimization.evaluation import BPCY, WYIELD, AggregatedSum
f1 = BPCY(biomass_reaction_id,product_reaction_id,method ='lMOMA')
f2 = WYIELD(<biomass_reaction_id>,<product_reaction_id>)

fevaluation = AggregatedSum([f1,f2],tradeoffs=[0.7,0.3])
```
