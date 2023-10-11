# Add Splitting Method

To add a new edge splitting method follow these steps:

1. Fork the dataset, pull the latest changes and create a new branch 
***add-splitting-{split_name}***

2. In the `framework/dataloader/edge_splitter/edge_splitter.py` implement a function that performs the splitting.
   * This function must return a list of edges of type `t.List[t.Tuple[UserNode, ItemNode]]` 

3. In the same file, add the splitting method name to the list ***self.supported_methods***.  

4. Add the splitting method into `split()`.
    * Add the method to the switch case.
    * Make sure to check if the parameters are valid. Otherwise, a `ValueError` must be raised.

5. Make a Pull Request on Github.