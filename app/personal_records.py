def runPlot():
        
    import streamlit as st
    import time as time
    import datetime
    import requests 
    import numpy
    import pandas as pd
    import numpy as np
    from pandas.io.json import json_normalize
    from PIL import Image


    SkaterLookupURL = "https://speedskatingresults.com/api/json/skater_lookup.php"
    PersonalRecordsURL =  "https://speedskatingresults.com/api/json/personal_records.php"


    #Retrieving skaters by firstname and lastname
    def getSkaters(givenname,familyname):
        parameters = {'givenname':givenname,'familyname':familyname} 
        r = requests.get(url = SkaterLookupURL, params = parameters) 
        data = r.json() 
        results = json_normalize(data)
        resultsNormalized = pd.io.json.json_normalize(results.skaters[0])

        return resultsNormalized

    #Retrieving Skater ID of the chosen skater (in the side menu)
    def findSkaterID(chosenSkater, skatersFormatted,skaterListID):
        search = skatersFormatted.str.find(chosenSkater)
        listIndex = np.where(search == 0)
        skaterID = skaterListID[listIndex[0]]

        return int(skaterID)
    #Sidenar inputs for skaters
    st.sidebar.header("Zoeken:") 
    givenname = st.sidebar.text_input('Voornaam')
    familyname = st.sidebar.text_input('Achternaam')

    #Retrieving skaters with user input
    skaterDoesntExist = False
    try: 
        skatersList = getSkaters(givenname,familyname)
        skatersFormatted = skatersList['givenname']+ ' ' +  skatersList['familyname'] + ' (' +  skatersList['country'] + ')'
        skaterListID = skatersList['id']
    except:
        skaterDoesntExist = True
    
    st.title("Persoonlijke Records")
    #Error if skater the user searched for does not exist
    if skaterDoesntExist == True:
        st.warning("Fout: Deze schaatser is niet gevonden op speedskatingresults.com")
    else:
            
        #Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatster',skatersFormatted)

        #Getting Skater ID of chosen 
        SkaterID = findSkaterID(chosenSkater,skatersFormatted,skaterListID)

        # Retrieving records using API
        Parameters = {'skater':SkaterID} 
        r = requests.get(url = PersonalRecordsURL, params = Parameters) 
        data = r.json() 

        # Json to dataframe
        df = json_normalize(data)

        # Json column to new dataframe
        dfNormalized = pd.io.json.json_normalize(df.records[0])

        #Results
        if not dfNormalized.empty:
            distances = dfNormalized['distance'].values.tolist()

            times = dfNormalized['time'].values.tolist()

            # Info
            st.info("Schaatser: " + str(chosenSkater) + "   \nSkaterID: " + str(SkaterID))
            dfNormalized = dfNormalized.rename(columns={"date": "Datum", "distance": "Distance", "location": "Locatie","time": "Record tijd"})
            dfNormalized = dfNormalized[["Distance","Record tijd","Datum","Locatie"]]
            dfNormalized['Distance'] =  dfNormalized['Distance'].astype(str)+ "m"
            st.table(dfNormalized.set_index("Distance"))
            
        else: 
                st.header("Geen data") 











