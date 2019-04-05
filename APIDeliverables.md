# AI for Earth - API Deliverables

Select AI for Earth grant recipients are contributing AI for Earth APIs.  If you are providing an API, here are the specific deliverables to submit:

+ [Container with machine learning model](#container)
+ [Jupyter notebook (for demo suite)](#notebook)
+ [Documentation](#doc)
+ [Assets for website](#assets)

The container should be uploaded to a container registry (more details below).  The Jupyter notebook, documentation, and website assets should be submitted via pull request to a private git repo at https://aiforearth.visualstudio.com/_git/AIforEarth-API-Push.  

Prior to submitting your work, you will need to contact us to provide the email address of the individual who will own uploading to the git repository above and to the container registry.  This is in order to grant appropriate permissions.  Please email aiforearthcommunity@microsoft.com with the subject line = "API push request" and the body of your email containing the email address of the person who will be responsible for submission.  

If you have questions, please contact aiforearthcommunity@microsoft.com.  


## <a name="container">Container with machine learning model</a>
The actual delivery of your API can be done via a Docker container.  
+ Please follow the directions [here](./Quickstart.md) to create the Docker container.  
    + In step 8, when you build your Docker image, please tag it using the tag:
		“ai4egrantee.azurecr.io/<grantee_moniker>/<image_version>-<api_name>:<build_number>”
	+ Replace step 10-11 with publishing to our AI for Earth container registry.  Use the following commands:
    ```
	docker login --username <username> --password <password> ai4egrantee.azurecr.io
	docker push ai4egrantee.azurecr.io/<grantee_moniker>/<image_version>-<api_name>:<build_number>
    ```
+ Please send an email to aiforearthcommunity@microsoft.com with the subject line = "API push request" and the body of your email containing the email address of the person who will push the container (so we can grant that email address the appropriate permissions to push to our container registry).  
+ In terms of testing, please ensure that your code meets the defined [acceptance criteria](./AcceptanceCriteria.md).  

**Alternate option:** People can either provide a container that meets the acceptance criteria, or they can relax/lower the bar on acceptance criteria and provide their source code with a semi-functional container.


## <a name="notebook">Jupyter Notebook</a>
We are compiling a suite of demos, to showcase the work of our AI for Earth grant recipients.  These demos are intended for an audience of developers and data scientists, so they can see how to call your API and the type of results that your machine learning model returns.  Please include sample data for calling your API that can be publicly shown.  
+ Please follow the directions [here](./JupyterNotebook.md) to create a Jupyter notebook that can be used to demonstrate your amazing work.  
+ We have also provided a [template notebook](./Notebooks/template-demo.ipynb) that you can start from.  


## <a name="doc">Documentation</a>
Of course, every good API needs documentation to show its usage.  Please include any assumptions that your code makes (for example, all input images must be square tiles) and an example of how to call the API.  
+ Please provide documentation of your API using the [OpenAPI specification](https://swagger.io/specification/), as a .json file.  
+ We recommend that you build and validate it using the [Swagger Editor](https://editor.swagger.io/).  You can start with the example that they provide or with [our landcover mapping documentation](./Documentation/landcover_api_spec_swagger.0.1.json) as an example.  
+ The final product (rendered on the website) will look like this, for an example of useful information to include (click on the version numbers): https://aka.ms/aieapisdoc 

Additional resources that may be useful
+ This is the process that we will follow to import your API: https://docs.microsoft.com/en-us/azure/api-management/import-and-publish#a-namecreate-api-aimport-and-publish-a-backend-api 
+ This link documents the API import restrictions and known issues for OpenAPI/Swagger: https://docs.microsoft.com/en-us/azure/api-management/api-management-api-import-restrictions 
+ Important information and tips related to OpenAPI import: https://blogs.msdn.microsoft.com/apimanagement/2018/04/11/important-changes-to-openapi-import-and-export/ 


## <a name="assets">Assets for website</a> 
These assets could potentially be used on the AI for Earth website to highlight your API.  For an example, see https://aka.ms/AI4EAPI.  

Please provide the following:
+ Image (high-resolution; we will crop to the right size)
+ Three-line summary of API (300 characters maximum)
+ Link (to follow on the “Learn about X”)  
