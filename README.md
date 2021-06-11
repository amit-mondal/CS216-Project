# CS216-Project
An implementation of TCAM nearest-neighbor search (https://dl.acm.org/doi/abs/10.1145/2771937.2771938) using P4 as a TCAM simulator

### How to Run

First, set up your environment by following the instructions for "Obtaining required software" [here](http://https://github.com/p4lang/tutorials "here:")

Then, clone this repo and run `setup.sh`.

Enter the `tutorials/exercises/tcam` directory and run `python generate_p4.py > calc.p4`. Run `make` to enter the Mininet console, and then run `h1 python tcam.py` to run the nearest-neighbor search on a random query point.

### Configuring Params
Set the `points` variable in `generate_p4.py` to manually set the dataset to search over, or set `RANDOM_PTS` to true and `NPOINTS` to the desired number of search points to randomly generate a dataset.

All the variables described in the paper, such as the number of hypercubes per point, the maximum search range, the range of the dataset, and the dimensionality of the data are all set in `generate_p4.py`. The number of bits to use in each TCAM entry is `MAX_BITS` in `p4template.py`.

If `RANDOM_PTS` is true, then you can run `tcam.py` without any parameters, and it will chose a random query point to search for. If you want to choose your own query point, pass each dimension as a command line argument like so: `tcam.py 45 23 67`.
