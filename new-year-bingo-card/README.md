# Holiday Bingo

## Overview

The Holiday Bingo Generator is a Python web application built with [H2O Wave](https://wave.h2o.ai) that serves as a user-friendly interface for creating personalized Bingo Cards based on free-text descriptions of users' 2024 goals. The idea is to make the process of tracking and achieving goals more engaging by presenting them in a fun and interactive way. Users can generate a printable Bingo Card, hang it on their wall, and mark off accomplished goals as they progress throughout the year.

You can try the app out yourself for free using your Gmail or Github account at 
https://2024-bingo.genai.h2o.ai. 

Developers can use this app as a template of a custom UI on top of any collections 
of data in h2oGPTe. Try making an app with your own special Bingo theme such 
as "Meeting Bullshit Bingo"!

## Features

- **Text-to-Bingo Conversion:** The application leverages a Language Model (LLM) to analyze free-text input and convert it into Bingo card content. The LLM understands your goals and creates a unique Bingo card tailored to your aspirations.

- **Customizable Bingo Cards:** Users have the flexibility to customize their Bingo Cards by editing, adding, or removing goals. The goal is to create a visually appealing card that motivates and inspires.

- **Printable and Shareable:** Once the Bingo Card is generated, users can easily print it out and hang it on their wall. The printable version is designed to be aesthetically pleasing, featuring a clean layout and vibrant colors.

- **Progress Tracking:** The Bingo Card serves as a visual representation of the user's goals. As goals are achieved, users can mark them off directly on the printed card, creating a tangible and satisfying record of progress.

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
    cd genai-app-store-apps/financial-research
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
   
7. Add SEC-10Ks to your H2OGPTE account:

    Each SEC-10K can take up to 5 minutes to upload and embed. Overall this step can 
    take up to two hours. 
    ```shell script
    python utilities/upload.py 
    ```
   
### Usage

1. Enter your 2024 goals in the provided text box.
2. Click the "Generate Bingo Card" button.
4. Review the generated Bingo Card and make any final adjustments by changing to Edit Mode.
5. Screenshot your Bingo Card to print or share with friends.

Hang your Bingo Card on your wall, and start marking off goals as you achieve them!

### Deploy

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

```shell script
echo "Setting variables for this app"
app_name=ai.h2o.wave.bingo_new_years_cards;
app_alias=2024-bingo;

echo "Fetching IDs of previous app version and instance"
old_app_id=$(genai app list --name $app_name -l | awk 'NR==2{print $1}');
old_instance_id=$(genai instance list $old_app_id | awk 'NR==2{print $1}');

echo "Importing and running the new app version"
genai bundle import -v PUBLIC;
new_app_id=$(genai app list --name $app_name -l | awk 'NR==2{print $1}');
new_instance_id=$(genai app run $new_app_id -v ALL_USERS | awk 'NR==1{print $2}');

echo "Assigning the alias to the new app version"
genai admin alias assign $app_alias $new_instance_id True;

echo "Privating the previous app version and instance - do not delete without testing!!"
genai admin app update -v PRIVATE $old_app_id
genai admin instance update -v PRIVATE $old_instance_id
```

## Contributing

Contributing to this project is welcome! You can open a PR with suggested changes or 
improvements to this specific app, or create your own GenAI app using this one as a 
template.


## Acknowledgments

Special thanks to the developers of 
[H2OGPTE](https://h2o.ai/platform/enterprise-h2ogpte/) for creating RAG capabilities 
and [H2O Wave](https://wave.h2o.ai) for the ability to rapidly develop web apps using 
only Python.

Enjoy tracking and achieving your goals with the GoalTracker Bingo Generator!