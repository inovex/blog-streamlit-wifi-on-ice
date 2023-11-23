# Wifi on ICE

## Overview
This is the repo for the blog post ...

In this blog post, we're getting hands-on. We're building a data app using Streamlit directly from Snowflake on a dataset of the Deutsche Bahn. So, hold onto your seats – it's time to explore the world of data apps with Deutsche Bahn.

## Contents

1. **Data**
   - The `./data/preprocessed_wifi_data.csv` file contains sample data related to Wifi usage on Deutsche Bahn trains. It includes information on averaged data rate consumption per logged-in device for different routes.
2. **Script**
   - The `./app/wifi_on_ice_app.py` script is the main Python script for the Streamlit app. 
## Requirements

To run the Streamlit app in Snowsight, make sure you have a Snowflake account with appropriate permissions (CREATE STRAMLIT privilege) 
As we plan to use Streamlit integration, the Snowflake account is required to be located in an Amazon Web Services (AWS).

## Getting Started
Firstly, upload the `./data/preprocessed_wifi_data.csv` file in Snowsight.
Follow these steps: 
1. Navigate to the “Data” tab on the left in Snowsight
2. Choose a database or create one
3. Click on "Create" -> "Table" -> "From file" to upload the csv-file from your local source
4. Adjust data formats and other settings to ensure accurate ingestion 
5. Optionally, you might need to select a specific warehouse based on your requirements

For more detailed information and guidance, refer to the [Snowsight documentation](https://snowflake.community.snowflake.com/s/article/Snowsight-User-Guide).

Secondly, paste the `./app/wifi_on_ice_app.py` in the Snowsight's Python editor
Follow these steps: 
1. Navigate to the “Streamlit” tab on the left in Snowsight.
2. Click on “+ Streamlit App” and provide a name “WIFI on ICE” for the app 
3. Chose the previous warehouse and app location
4. Click on “Create”
5. Paste the content of `./app/wifi_on_ice_app.py` in the Edior
6. Start the app by clicking on "Run"

## License 
The used dataset is provided under the Creative Commons Attribution 4.0 International License (CC BY 4.0), see [Wifi on ICE Dataset](https://data.deutschebahn.com/dataset/wifi-on-ice.html).



