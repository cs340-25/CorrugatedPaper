from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import csv

# Configure Chrome
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options)

try:
    # Load CAS login page
    print("Loading CAS login page...")
    driver.get("https://cas.tennessee.edu/cas/login?TARGET=https%3a%2f%2fmyutk.utk.edu%2fCASLogin.aspx")
    print("Please log in manually in the browser window...")
    
    # Wait for manual login completion
    login_wait = WebDriverWait(driver, 300)  # 5 minute timeout
    login_wait.until(lambda d: "myutk.utk.edu/Home.aspx" in d.current_url)
    print("Login successful! Current URL:", driver.current_url)
    
    # Go to term selection page
    print("Navigating to term selection...")
    driver.get("https://bannerreg.utk.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search")
    
    # Wait for term selection page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "txt_term"))
    )
    print("Term selection page loaded")
    
    # Select Fall 2025 term
    term_value = "202540"
    driver.execute_script(f"""
        document.querySelector('#txt_term').setAttribute('listofsearchterms', '{term_value}');
    """)
    
    # Click Continue button
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "term-go"))
    )
    continue_button.click()
    print("Clicked Continue button")
    
    WebDriverWait(driver, 20).until(
            lambda d: d.find_elements(By.ID, "search-go") or d.find_elements(By.CLASS_NAME, "error-message")
    )
    
    # Get session ID from cookies
    session_cookie = driver.get_cookie("JSESSIONID")
    if not session_cookie:
        raise Exception("Could not find session cookie")
    session_id = session_cookie["value"]
    print(f"Session ID: {session_id}")
    
    # Build the search URL
    base_url = "https://bannerreg.utk.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"
    params = {
        "txt_term": term_value,
        "startDatepicker": "",
        "endDatepicker": "",
        "uniqueSessionId": session_id,
        "pageOffset": "0",
        "pageMaxSize": "500",
        "sortColumn": "subjectDescription",
        "sortDirection": "asc"
    }
    
    # Get all of the class sections, and merge them with the CSV data to upload to MongoDB
    db_data = {}
    new_data = {}
    with open("backend/catalog.csv") as file:
        old_data = csv.DictReader(file)
        for row in old_data:
            db_data[row["prefix"] + row["code"]] = row
    
    for i in range(22):
        params["pageOffset"] = str(i*500)
        search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        # Make the API request
        driver.get(search_url)

        # Get the raw JSON response
        pre_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "pre")))
        json_data = pre_element.text

        # Parse the JSON
        try:
            data = json.loads(json_data)
            for i in data["data"]:
                if i["subject"] not in new_data:
                    new_data[i["subject"]] = {}
                if i["courseNumber"] not in new_data[i["subject"]]:
                    if i["subject"] + i["courseNumber"] not in db_data:
                        new_data[i["subject"]][i["courseNumber"]] = {
                            "subject": i["subject"],
                            "courseNumber": i["courseNumber"],
                            "courseTitle": i["courseTitle"],
                            "courseDescription": "Unknown",
                            "creditHours": i["creditHours"],
                            "prerequisites": "Unknown",
                            "corequisites": "Unknown",
                            "classes": []
                        }
                    else:
                        new_data[i["subject"]][i["courseNumber"]] = {
                            "subject": i["subject"],
                            "courseNumber": i["courseNumber"],
                            "courseTitle": db_data[i["subject"] + i["courseNumber"]]["course name"],
                            "courseDescription": db_data[i["subject"] + i["courseNumber"]]["description"],
                            "creditHours": db_data[i["subject"] + i["courseNumber"]]["credit hours"],
                            "prerequisites": db_data[i["subject"] + i["courseNumber"]]["prereqs"],
                            "corequisites": db_data[i["subject"] + i["courseNumber"]]["coreqs"],
                            "classes": []
                        }

                new_data[i["subject"]][i["courseNumber"]]["classes"].append(i)
                
        except json.JSONDecodeError:
            print("Could not parse JSON response")

    data_array = [course for subject in new_data.values() for course in subject.values()]
    
    # Open MongoDB and write the data
    uri = "mongodb+srv://root:root@cluster0.cnbie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        exit()

    db = client.classes

    collection_name = "course"
    collection = db[collection_name]
    collection.delete_many({})

    collection.insert_many(data_array)

    client.close()
        

except Exception as e:
    print(f"An error occurred: {e}")