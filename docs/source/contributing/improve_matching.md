# Improve matching with DBpedia

Currently, the matching between an item dataset and DBpedia's resource is done using regex, but this approach is prone to errors and no manual inspection was done. If you were using this project and noticed that a dataset item was wrongly assigned to a DBpedia resource or wasn't matched, please consider making an issue.

Otherwise, if you figured out another approach that would be better to match RS dataset's items, please consider making an issue to discuss your new approach.

## Guide for wrongly matched/unmatched items

1. Create an issue describing:
   * Dataset name
   * Which item is wrongly matched or unmatched
   * Which DBpedia's resource is being matched.
   * Which DBpedia's resource should be matched.

2. Make the necessary changes to the `map.csv` corresponding to the mentioned dataset, changing only the `URI` field.
   * **Note:** the `map.csv` file can be found at `datasets/{dataset_name}/processed/` folder.

2. Make a commit with your changes.

3. Make a Pull Request on Github mentioning the issue.
  

