# Ask H2O

## Overview
The Ask H2O app is a Python web application built 
with [H2O Wave](https://wave.h2o.ai) that serves as a user-friendly interface for 
learning more about the capabilities of specific H2O.ai products. It 
leverages a RAG (Retrieval-Augmented Generation) based Language Model 
to enhance the search and analysis of information with product documents.

You can try the app out yourself for free using your Gmail or Github account at 
https://ask-h2o.genai.h2o.ai. 

Developers can use this app as a template of a custom UI on top of any collections 
of data in h2oGPTe.

## Features
* **RAG-based Language Model:** Powered by a sophisticated RAG-based Language Model, 
the app allows users to interactively query and generate information from product documentation.
* **User-friendly Interface:** The web app provides a simple and intuitive interface, 
making it easy for users to input queries, explore results, and refine searches.
* **Search and Summarize:** Quickly search through product docs, retrieve relevant 
information, and generate concise summaries to aid in getting started with H2O technology.
* **Interactive Conversations:** Engage in interactive conversations with the 
RAG-based model to refine queries and receive context-aware responses.

## Get Started Developing

### Prerequisites
* Python 3.7+ 
* Pip (Python package installer)
* Virtualenv (optional but recommended)

### Installation
1. Clone the repository:
    ```shell script
    git clone https://github.com/h2oai/genai-app-store-apps
    ```

2. Navigate to this app's directory:
    ```shell script
    cd genai-app-store-apps/ask-h2o
    ```
   
3. Create a virtual environment (optional but recommended):
    ```shell script
    python -m venv venv
    ```
4. Activate the virtual environment:
    * On Windows:
    ```shell script
    venv\Scripts\activate
    ```
    * On Unix or MacOS:
    ```shell script
    source venv/bin/activate
    ```
5. Install the required dependencies:
   ```shell script
    pip install -r requirements.txt
    ```

6. Get an H2OGPTE License Key:
    * Navigate to the [H2OGPTE Free Trial](https://h2ogpte.genai.h2o.ai), or your own 
    H2OGPTE Environment
    * Click `Settings` from the left side-panel
    * Create and save a new API Key
    ```shell script
    export H2OGPTE_URL="https://h2ogpte.genai.h2o.ai"
    export H2OGPTE_API_TOKEN="***"
    ```
   
7. Add the Product Docs to your h2oGPTe account:

    Each product documentation can take up to 5 minutes to upload and embed. 
    Overall this step can take up to two hours. 
    ```shell script
    python src/setup-h2ogpte.py 
    ```
   
### Usage

1. Run the application:
    ```
    wave run app.py
    ```
2. Open your web browser and navigate to http://localhost:10101 to access the 
Digital Asset Research Assistant.

## Deploy

Deploy your app in the H2O AI Cloud. Please note, users of the https://genai.h2o.ai 
Free Trial cannot deploy apps themselves today. Any contributions to this or a new app 
will be reviewed and deployed by the H2O.ai team.

1. Review the `app.toml` and use the h2o admin CLI or admin UI to create any 
necessary App Secrets

2. Import the app and make the visibility Public

3. Run an instance with the ALL_USERS visibility

4. Assign the Alias to the new instance or create and assign an Alias

5. Pause and delete the only instance

6. Delete the old app version

## Contributing
Contributing to this project is welcome! You can open a PR with suggested changes or 
improvements to this specific app, or create your own GenAI app using this one as a 
template.

## Acknowledgments

Special thanks to the developers of 
[H2OGPTE](https://h2o.ai/platform/enterprise-h2ogpte/) for creating RAG capabilities 
and [H2O Wave](https://wave.h2o.ai) for the ability to rapidly develop web apps using 
only Python.
