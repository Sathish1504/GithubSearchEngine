import json
import requests
import pandas as pd



def getData(table, query, page, entries_per_page):

    #search for the top repositories
    api_url = f"https://api.github.com/search/repositories?q={query}&per_page={entries_per_page}&page={page}"

    #send get request
    response = requests.get(api_url)

    #check status code
    if response.status_code != 200:
        print("Error: ", response.status_code)
        return table, {}
    

    #get the json data
    data =  response.json()


    # General info
    metadata = {"Total Count": data["total_count"], "Incomplete Results": data["incomplete_results"]}

    # Repositories info
    for repository in data["items"]:
        name = repository["name"]
        repo_name = repository["full_name"]
        created_date = repository["created_at"]
        language = repository["language"]
        stars = repository["stargazers_count"]
        forks_count = repository["forks_count"]
        score = repository["score"]
        topics = repository["topics"]
        private = repository["private"]
        owner_name = repository["owner"]["login"]
        url = repository["html_url"]
        description = repository["description"]
        size = repository["size"]

        # Add the new row to the table using pandas concat
        table = pd.concat([table, pd.Series({"Name":name, "Repository Name":repo_name, "Created Date":created_date, "Language":language, "Stars":stars, "Forks Count":forks_count, "Score":score, "Topics":topics, "Private":private, "Owner Name":owner_name, "URL":url, "Description":description, "Size":size}).to_frame().T], ignore_index=True)

    
    return table, metadata
