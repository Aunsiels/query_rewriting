# Query Rewriting Experiments

This Github repository contains the implementation of the experiments used in:

```
@inproceedings{romero2020equivalent,
    title={Equivalent Rewritings on Path Views with Binding Patterns},
    author={Julien Romero and Nicoleta Preda and Antoine Amarilli and Fabian Suchanek},
    year={2020},
    eprint={2003.07316},
    archivePrefix={arXiv},
    primaryClass={cs.DB}
}
```

## Installation

### Requirements

Run:

```bash
pip3 install -r requimenents.txt
```

### PDQ

Go into the directory *benedikt* and run the command:

```bash
bash install.sh
```

## Using our implementation

The python class *Solver* in *smart_plan/solver.py* makes it easy to run our implemented solution. Functions and UIDs can be constructed using the associated class in *smart_plan/function.py* and *smart_plan/uid.py* and can be fed into a Solver object. Then, calling the method *solve* on that object with your query will construct a single equivalent rewriting.

## Real-World Web Services Function Definitions

The real-world web service function definitions are located into the directory *definition*. They are stored by category and by function.

## Run Experiments

### For Real-World Web Services

Our approach:

```bash
python3 smart_plan/experiments.py 
```

For Susie:

```bash
python3 smart_plan/experiments_susie.py
```

For PDQ:

```bash
python3 smart_plan/experiments_benedikt.py 
```


### For Random Experiments

Run:

```bash
python3 smart_plan/experiments_random.py
```

## Run tests

Run:

```bash
pytest --showlocals -v smart_plan
```
