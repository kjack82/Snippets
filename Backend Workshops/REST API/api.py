from fastapi import FastAPI
import json

app = FastAPI()

# Load seed data from JSON file
with open('seedData.json', 'r') as f:
    snippets = json.load(f)

# Generate a unique ID for each snippet
id = len(snippets) + 1


## CREATE A NEW SNIPPET
@app.post("/snippet") 
def create_snippet(language: str, code: str): #function - both language and code will be strings
    if not language or not code: #validating, if here's no language, or code
        return {"error": "Language and code are required fields"}, 400 ##return an error 

    snippet = {  #otherwise lists what is expected when adding 
        "id": id, 
        "language": language,
        "code": code
    }
    snippets.append(snippet) ##append (add) to the end of the array 
    return snippet, 201 #return code 201 to confirm success 


##GET ALL SNIPPETS 
@app.get("/") 
def get_all_snippets():
    return snippets

## GET ALL SNIPPETSBY LANGUAGE
@app.get("/snippet")    ## GET request 
def get_snippets(language: str = None): #function to get snippets for which query parameter is the language 
    if language: #if there is a langauage 
        return [snippet for snippet in snippets if snippet["language"].lower() == language.lower()] #iterate through snippets, taking to lower case, if it matches the langauage 
    return snippets ##return details 

## can also do this way FOR LANGAUAGE 
@app.get("/snippet/language/{language}")
def get_snippets_by_language(language: str):
    filtered_snippets = [snippet for snippet in snippets if snippet["language"].lower() == language.lower()]
    if not filtered_snippets:
        return {"error": "Snippets not found"}, 404
    return filtered_snippets


## GET SNIPPET BY ID 
@app.get("/snippet/{id}") # add ID to query 
def get_snippet(id: int): #noting id will be integer 
    snippet = next((s for s in snippets if s["id"] == id), None) ## next is built in function - this will find the first snippet where the id matches in the list - iterating through the list 
    ##however if no match then returns none
    if not snippet: 
        return {"error": "Snippet not found"}, 404 ##returns error if none 
    return snippet #otherwise returns snippet 

    


    

    