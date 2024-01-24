# Notes
First meeting tech team (Tobi, Beni).
plan to programm a scraper that updates product entries 
via woocomerce REST API for conda.ch.

### Scraper
- all active projects scrape
    - create a new entry for each
    - update exisiting entries
    - update active state
- notfication email new entry
- update csv with properties (compare with existing projects)
    - manual assignment of properties
    - including category and upload yes/no

### Website Updater
- for all new yes: create project via API
    - add project ID to csv
- for all changed properies:
    - update via API
    - if inactive: delete via API
- for all projects update changed properties.

## Project properties to send
name -> parse
image -> parse
tags -> try to parse on website (default: ... )
type -> 'crowdfunding'
categories -> manual
images (list) -> Over Wordpress Rest API upload and get URL
meta_data (list) -> 
                 id: ... ,
                 key: krowd_project_link,
                 value: external project URL

## Per Project on rockets.
Title
Categories
Minimum Funding
Remaining Time

# Websites
https://www.biovision.ch/alle-projekte/
https://www.conda.ch/projekte-entdecken/
Website: rockets.investments
Min Funding Target: 250 Euro? or project specific?


