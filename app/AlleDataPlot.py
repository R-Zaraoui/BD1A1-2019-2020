
def runPlot():
    import streamlit as st
    import numpy as np
    import requests 
    import pandas as pd
    from pandas.io.json import json_normalize

    # Progress bar, status text, checking distance
    progress = 0
    progress_bar = st.sidebar.progress(progress)
    status_text = st.sidebar.empty()
    checkingDistance = st.sidebar.empty()


    SkaterLookupURL = "https://speedskatingresults.com/api/json/skater_lookup.php"
    URL =  "https://speedskatingresults.com/api/json/skater_results.php"


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


    #List of distances
    distances = [100,
        200,
        300,
        400,
        500,
        700,
        1000,
        1500,
        3000,
        5000,
        10000]
    
    # Sidebar inputs for skaters
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

    #Error if skater the user searched for does not exist
    if skaterDoesntExist == True:
        st.warning("Fout: Deze schaatser is niet gevonden op speedskatingresults.com")
    else:

        #Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatster',skatersFormatted)

        #Getting Skater ID of chosen skater
        SkaterID = findSkaterID(chosenSkater,skatersFormatted,skaterListID)

        emptydistances = []
        
        st.markdown("### " + 'Filter data')

        #Set filter box
        selected = st.selectbox(
            label="Selecteer...", options=['Alle data','Olympische Wedstrijden','Wereld Kampioenschappen','Europese Kampioenschappen', 'Nationale Kampioenschappen', 'Wereld Cup', 'Overige Evenementen']
        )
        for distance in distances:
            Distance = distance
                        
            # Set checking distance
            checkingDistance.text("Checking Afstand: %im " % distance)

            # Retrieving data using API
            Parameters = {'skater': SkaterID, 'distance': Distance}
            r = requests.get(url=URL, params=Parameters)
            data = r.json()

            # Json to dataframe
            df = json_normalize(data)

            # Json column to new dataframe
            dfCompetitions = pd.io.json.json_normalize(df.results[0])

            dfCompetitions = dfCompetitions.rename({"name": "Event"}, axis="columns")

            dfCompetitions['Soort evenement'] = ''

            # Determine type of event based on event name
            for index in range(len(dfCompetitions)):
                if 'olymp' in (dfCompetitions['Event'][index].lower()):
                    dfCompetitions['Soort evenement'][index] = 'Olympische Wedstrijden'
                if 'championship' in (dfCompetitions['Event'][index].lower()):
                    if 'world' in (dfCompetitions['Event'][index].lower()):
                        dfCompetitions['Soort evenement'][index] = 'Wereld Kampioenschappen'
                    else:
                        if 'euro' in (dfCompetitions['Event'][index].lower()):
                                dfCompetitions['Soort evenement'][index] = 'Europese Kampioenschappen'
                        else:
                            dfCompetitions['Soort evenement'][index] = 'Nationale Kampioenschappen'
                else:
                    if 'cup' in (dfCompetitions['Event'][index].lower()) and 'world' in (dfCompetitions['Event'][index].lower()) :
                        dfCompetitions['Soort evenement'][index] = 'Wereld Cup'
                    else:
                        if 'olymp' not in (dfCompetitions['Event'][index].lower()):
                            dfCompetitions['Soort evenement'][index] = 'Overige Evenementen'
            
            if selected != 'Alle data':
                dfCompetitions = dfCompetitions[dfCompetitions['Soort evenement'] == selected]
            
            dfCompetitions = dfCompetitions.reset_index(drop=True)
            if not dfCompetitions.empty:
                
                st.write(str(Distance) +'m:')

                dfCompetitions = dfCompetitions.rename(columns={"time": "Gereden tijd", "date": "Datum", "Event": "Toernooi","location": "Locatie",'link':'Link'})

                def make_clickable(link):
                    # target _blank to open new window
                    # extract clickable text to display for your link
                    text = 'Toernooi link'
                    return f'<a target="_blank" href="{link}">{text}</a>'

                # link is the column with hyperlinks
                dfCompetitions['Link'] = dfCompetitions['Link'].apply(make_clickable)
                
                dfCompetitions2 = dfCompetitions.to_html(escape=False)

                st.write(dfCompetitions2, unsafe_allow_html=True)
            else:
                emptydistances.append(distance)            
                # If empty distances contain all distances
                if emptydistances == distances:
                    st.error("Geen data     \n Voeg data toe voor " + str(chosenSkater) +
                            " op speedskatingresults.com om hier een grafiek te plotten")
            # Set progressbar
            if progress == 90:
                progress = 100
            else:
                progress += 9
            progress_bar.progress(progress)
            status_text.text("%i%% Compleet" % progress)

            # Set checking distance
            if distance == 10000:
                checkingDistance.empty()
