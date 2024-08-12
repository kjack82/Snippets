from fastapi import FastAPI, HTTPException, Query
import json #required to parse data between files 
from cryptography.fernet import Fernet  ##required for encryption
import base64 ##required for encryption
from user_router import router as user_router


app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["user"])

# test_message = "Does this work?"

key = Fernet.generate_key() #used to generate a key for encryption
fernet = Fernet (key) ## instance the fernet class with the key 

# encMessage = fernet.encrypt(test_message.encode())  >> used as a test in regards to encrypting a message only first 
# print("original string: ", test_message)
# print("encrypted string: ", encMessage)
# decMessage = fernet.decrypt(encMessage).decode()
# print("decrypted string: ", decMessage)


snippets = []  #snippets = empty list
with open('seedData.json', 'r') as file: #open seedData.json file, and read as file (alias)
    seed_snippets = json.load(file) ## seed snippets = loaded file 
    for snippet in seed_snippets:  #for loop, for snippet in seed snippets
        snippet_bytes = json.dumps(snippet).encode() ##json function to convert subset of python objects to a json string
        encrypted_data = fernet.encrypt(snippet_bytes) ##then encrypt that string
        encoded_data = base64.urlsafe_b64encode(encrypted_data).decode() ##encodes the string, safely. 
        snippets.append(encoded_data)    #adds encoded string to the list from seed json file 
    

# Generate a unique ID for each snippet
id = len(snippets) + 1 

## CREATE A NEW SNIPPET 
@app.post("/snippet") 
def create_snippet(language: str, code: str): #function - both language and code will be strings
    if not language or not code: #validating, if here's no language, or code
        raise HTTPException(status_code=400, detail="Require language and code")##return an error 

    snippet = {  #otherwise lists what is expected when adding 
        "id": id, 
        "language": language,
        "code": code
    }
    
    snippet_bytes = json.dumps(snippet).encode() ##json function to convert subset of python objects to a json string
    encrypted_data = fernet.encrypt(snippet_bytes)  # Encrypt the data
    encoded_data = base64.urlsafe_b64encode(encrypted_data).decode()   # Encode the encrypted data in base64

    snippets.append(encoded_data) ##add the new snippet (encoded) to the end 
    return {"snippet encoded successfully": encoded_data} #return encoded data

##GET ALL SNIPPETS 
@app.get("/snippets")
def get_all_snippets():
    decoded_snippets = []
    for encoded_snippet in snippets:
        try:
            encrypted_data_bytes = base64.urlsafe_b64decode(encoded_snippet) ## Decode the base64 encoded string to bytes
            decrypted_data = fernet.decrypt(encrypted_data_bytes) #ensure data is decrypted
            snippet_str = decrypted_data.decode() #convert decrypted bytes back to string - then to dictionary 
            snippet = json.loads(snippet_str)  # Safe parsing
            decoded_snippets.append(snippet) #add parsed snippets to list of decoded snippets 
        except Exception as error:
            raise HTTPException(status_code=500, detail="Error decoding and obtaining snippets")

    return decoded_snippets

##GET A SNIPPET OR SNIPPETS BY ID OR LANGUAGE 
@app.get("/snippet")
def get_snippet(encoded_snippet: str = Query(None), id: int = Query(None), language: str = Query(None)): #Search queries, however all search fields optional 
        if encoded_snippet:  
            encrypted_data_bytes = base64.urlsafe_b64decode(encoded_snippet) # Decode the base64 encoded string to bytes
            decrypted_data = fernet.decrypt(encrypted_data_bytes)# Decrypt the data
            snippet_str = decrypted_data.decode() # Convert the decrypted bytes back to string and then to a dictionary
            snippet = json.loads(snippet_str)  # Safe parsing
            return snippet
        elif id is not None:
            for encoded_snippet in snippets:
                encrypted_data_bytes = base64.urlsafe_b64decode(encoded_snippet)# Decode the base64 encoded string to bytes
                decrypted_data = fernet.decrypt(encrypted_data_bytes) # Decrypt the data
                snippet_str = decrypted_data.decode() # Convert the decrypted bytes back to string and then to a dictionary
                snippet = json.loads(snippet_str)  # Safe parsing
                if snippet['id'] == id: # if id matches that input - return the relevant snippet using id 
                    return snippet
            raise HTTPException(status_code=404, detail="Snippet not found") #else return an error 
        elif language: #else if searching by language 
            filtered_snippets = [] #create new list 
            for encoded_snippet in snippets:
                encrypted_data_bytes = base64.urlsafe_b64decode(encoded_snippet)  # Decode the base64 encoded string to bytes
                decrypted_data = fernet.decrypt(encrypted_data_bytes)  # Decrypt the data
                snippet_str = decrypted_data.decode() # Convert the decrypted bytes back to string and then to a dictionary
                snippet = json.loads(snippet_str)  # Safe parsing
                if snippet['language'].lower() == language.lower(): #check all at lower case 
                    filtered_snippets.append(snippet) #if find language - add to new list
            if not filtered_snippets:
                raise HTTPException(status_code=404, detail="No snippets found for the specified language") #if none, error message 
            return filtered_snippets #otherwise return filtered snippets for language 
        else:
            raise HTTPException(status_code=400, detail="Query parameter required") #if none entered, error to advise of this 
    
@app.delete("/snippet")
def delete_snippet(id: int = Query(None), encoded_snippet: str = Query(None)):
    if id is None and encoded_snippet is None:
        raise HTTPException(status_code=400, detail="Ensure ID or code snippet is entered")
    
    if id is not None:
        for i, encoded_data in enumerate(snippets):
            encrypted_data_bytes = base64.urlsafe_b64decode(encoded_data)
            decrypted_data = fernet.decrypt(encrypted_data_bytes)
            snippet_str = decrypted_data.decode()
            snippet = json.loads(snippet_str)  # Safe parsing
            if snippet['id'] == id:
                del snippets[i]
                return {"message": f"Snippet ID {id} has been deleted"}
        raise HTTPException(status_code=404, detail="Unable to lcoate snippet")
    
    if encoded_snippet:
        for i, encoded_data in enumerate(snippets):
            if encoded_data == encoded_snippet:
                del snippets[i]
                return {"message": "Snippet has been deleted"}
        raise HTTPException(status_code=404, detail="Unable to locate snippet")

