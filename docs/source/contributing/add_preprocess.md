# Add Pre-processing method

To add a pre-processing method follow these steps:

1. Fork the dataset, pull the latest changes and create a new branch ***add-preprocess-{method_name}***

2. In the `framework/dataloader/preprocess/methods.py` implement a function that performs the pre-processing method.

3. In the same file, add the pre-processing method to the dictionary ***method2fun***, `method_name: method_function`.  
   - The key must be the pre-process method name. This name will be used by the framework to call the function.
   - The value is the function itself.
   - Example:
   ```python
    method2fun = {
        # .....
        # method_name: method_function
        'binarize': binarize,
    }
   ```

4. Make a Pull Request on Github.