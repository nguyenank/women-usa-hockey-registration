# Women's USA Hockey Registration

This repo provides the source code for the data collection/cleaning and app visualization ([web version here](http://women-usa-hockey-registration.herokuapp.com/)) of USA Hockey registration data of girls/women by state since 1991.

## App

The visualization app, created using Plotly/Dash, is the bulk of the root of the repo. Details about what exactly is included in the repo are below:

-   `app.py` - the actual webapp
-   `components.py` - contains code for creating most of the components (choropleth map, sliders, etc.) used in the app
-   `Procfile` - server details, needed for running the app on Heroku
-   `requirements.txt` - all the packages necessary for the app; needed for running the app on Heroku
-   `.gitignore/.slugignore` - files to not be saved by Git/Heroku respectively
-   :open_file_folder: `assets` - assets to be available to the webapp
    -   `app.css` - CSS styling for the app
-   :open_file_folder: `data` - data used in the app
    -   :file_folder: `06-20` - absolute and percent change data for 2006-2020
    -   :file_folder: `91-04` - absolute and percent change data for 1991-2004
    -   :file_folder: `districts` - absolute and percent change data for the USA Hockey districts after 2007
    -   `girls-women-by-district-by-state.pkl` - data of girls/women enrollment by district and by state since 1991
    -   `districts02-06.geojson` - encodes the geographical districts of USA Hockey from 2002 to 2006 (**Note:** I believe these districts are accurate for years prior to 2002 as well, but that is when district level data for girls/women is available from. Also, this file is not currently used in the app.)
    -   `districts07-20.geojson` - encodes the geographical districts of USA Hockey from 2007 to 2020
    -   `states.geojson` - encodes the states as denoted by USA Hockey since 2005, which includes Washington D.C. (DC), as well as East and West Pennsylvania (E PA and W PA)
-   :file_folder: `source` - contains the source code for data collection and cleaning; contents described in more detail below

## Source Code for Data Collection/Cleaning

The source code for collection and cleaning the data is contained in the :file_folder: `source` folder of the repo. Some of what is included overlaps with what is contained in the :file_folder: `./data` folder. Details about what is in the :file_folder: `source` folder is below:

-   `extract_tables.py` - all of the code for extracting and processing the data (**Note:** this file requires some packages that are not listed in `./requirements.txt` or elsewhere in the repo.)
-   :open_file_folder: `data` - the data for and/or generated in the process of cleaning
    -   :file_folder: `pkls` - data in pickle (.pkl) format; all files contained here can also be found in the :file_folder: `./data` folder
    -   :file_folder: `geojsons` - geojsons; all files contained here can also be found in the :file_folder: `./data` folder
    -   :file_folder: `pdfs` - This folder normally contains all of the PDF versions of enrollment data from USA Hockey renamed to indicate the years (ex. the PDF with information about 2006-2007 registration numbers is located in here, renamed `06-07.pdf`). (**Note:** This folder is intentionally left empty; all PDFs should be acquired from the USA Hockey website.)
    -   :open_file_folder: `csvs` - data in .csv format
        -   :file_folder: `raw` - yearly data as initially read from the PDFs
        -   :file_folder: `cleaned` - yearly data as cleaned to fix formatting errors from the reading process
        -   :file_folder: `merged` - data from different years merged together; contains .csv version of all files found in :file_folder: `pkls`
