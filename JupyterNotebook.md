# AI for Earth - Creating a Jupyter Notebook Demo
The AI for Earth team is compiling a small suite of Jupyter Notebook demos.  These notebooks allow us to showcase the work of the AI for Earth grant recipients, and demonstrate the use of their machine learning models to benefit agriculture, water, climate, and biodiversity.  

This article will walk you through the creation of a Jupyter notebook.  You are also welcome to start with this [template notebook](./Notebooks/template-demo.ipynb).  

If you are already comfortable with Jupyter notebooks, you may create them however you'd like.  If you are new to them, you are welcome to try https://notebooks.azure.com/ to create a Jupyter notebook.  

You will also need to provide sample data to use in this demonstration.  Please ensure that it is data that can be shared publicly.  

## Outline

Here are the suggestions for the outline of your notebook.  
+ The first cell should be markdown, giving a title for your demo and a short description of what it does.  
+ The next two cells should be a markdown and corresponding code cell for imports and constants.  
+ The next two cells should be a markdown and corresponding code cell for helper functions.  Functions that retrieve data, display an image, plot data, etc. can live here.  
+ The next two cells should be a markdown and corresponding code cell to display your input, if needed.  In the situation of a computer vision problem like image classification, object detection, or segmentation, it is nice to first see the input image before we see your results.
+ Finally, the remaining cells can be used to call your machine learning model and show its results.  If you are not hosting it yourself, please ensure that you have provided a Docker container to us.  

## Guidelines

Please choose a descriptive name for your notebook (and any config files if needed).  The format organization-apiName-demo.ipynb would work well, where organization is your company or univeristy name and the api name describes the purpose of your machine learning model.  
	
We should get as close as we can to only three cells before the action happens: (1) one cell for constants, imports, and health check, (2) one cell for function definitions, and (3) one cell to retrieve and display sample input.  Each should have a ### heading saying what's going on, and in general those headings should be similar or identical across notebooks.  Merging into a small number of cells really streamlines the demo workflow and avoids lots of clicking.  

If there are details that you don't want to be visible to the audience during a demo (such as connection string information to an Azure blob storage account), you are welcome to provide a configuration file as well.  

When we log in to demo, output should be clear (it really steals the demo thunder when you see the API result before you call the API), so to disable autosave from saving the output, add %autosave 0.  This can be done in the "Imports and Constants" section.  
