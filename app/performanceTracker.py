
def runPlot():
    # Imports
    import streamlit as st
    import requests
    import pandas as pd
    import numpy as np
    from pandas.io.json import json_normalize
    import time as time
    import datetime
    import calendar
    import snelheidPlot
    import plotly.graph_objects as go
    from datetime import datetime as dt
    from bs4 import BeautifulSoup
    from scrapy import Selector

    #API source
    SkaterLookupURL = "https://speedskatingresults.com/api/json/skater_lookup.php"

    #Retrieving skaters by firstname and lastname
    def getSkaters(givenname, familyname):
        parameters = {'givenname': givenname, 'familyname': familyname}
        r = requests.get(url=SkaterLookupURL, params=parameters)
        data = r.json()
        results = json_normalize(data)
        resultsNormalized = pd.json_normalize(results.skaters[0])

        return resultsNormalized

    #Retrieving Skater ID of the chosen skater (in the side menu)
    def findSkaterID(chosenSkater, skatersFormatted, skaterListID):
        search = skatersFormatted.str.find(chosenSkater)
        listIndex = np.where(search == 0)
        skaterID = skaterListID[listIndex[0]]

        return int(skaterID)

    #Sidebar inputs for skaters
    st.sidebar.header("Zoeken:")
    givenname = st.sidebar.text_input('Voornaam')
    familyname = st.sidebar.text_input('Achternaam')

    #Retrieving skaters with user input
    skaterDoesntExist = False
    try:
        skatersList = getSkaters(givenname, familyname)
        skatersFormatted = skatersList['givenname'] + ' ' + skatersList['familyname'] + ' (' + skatersList['country'] + ')'
        skaterListID = skatersList['id']
    except:
        skaterDoesntExist = True
        
    #Error if skater the user searched for does not exist
    if skaterDoesntExist == True:
        st.warning("Fout: Deze schaatscher is niet gevonden op speedskatingresults.com")

    else:
        #Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatster', skatersFormatted)

        #Getting Skater ID of chosen 
        SkaterID = findSkaterID(chosenSkater, skatersFormatted, skaterListID)
        
        url = 'https://speedskatingresults.com/index.php?p=17&s=%d'%SkaterID
        getPage = requests.get(url) 
        
        soup = BeautifulSoup(getPage.text, 'html.parser') # 1
        
        sel = Selector(text=str(soup))
        date2 = sel.xpath('//*[@id="wrapper"]/main/div[1]/div[1]/h2/span/text()')\
        .extract_first()\
        .split()

        
        geboorte = int(date2[1])


        # Info
        st.info("Schaatser: " + str(chosenSkater) +
                "   \nSkaterID: " + str(SkaterID))
    
        start = 2007
        end = 2020
        Distance = st.sidebar.selectbox('Afstand', [
            1000,
            1500,
            3000,
            5000,
            10000,
            date2[0]+ " " + date2[1]
        ])
        Distance = int(Distance)

        # Retrieving Season bests results using API
        def getSBT(SkaterID, start, end, Distance):
            Parameters = {'skater': SkaterID, 'start': start,
                        'end': end, 'distance': Distance}
            # URL
            URL = "https://speedskatingresults.com/api/json/season_bests.php"
            r = requests.get(url=URL, params=Parameters)
            data = r.json()
            results = json_normalize(data)
            resultsNormalized = pd.json_normalize(results.seasons[0])

            return resultsNormalized

        # Retrieving World records using API
        def getWorldRecord(Gender, Age, Distance):
            Parameters = {'gender': Gender, 'age': Age, 'distance': Distance}
            # URL
            URL = "https://speedskatingresults.com/api/json/world_records.php"
            r = requests.get(url=URL, params=Parameters)
            data = r.json()
            results = json_normalize(data)
            resultsNormalized = pd.json_normalize(results.records[0])

            return resultsNormalized

        # Retrieving gender
        Gender = skatersList['gender'].iloc[0]

        # Retrieving age category
        catSkater = skatersList['category'].iloc[0]

        # Set ageCate to jr/sr
        ageCate = ''

        if catSkater == 'YF' or catSkater == 'YE' or catSkater == 'YD' or catSkater == 'YC' or catSkater == 'YB' or catSkater == 'YA' or catSkater == 'C1' or catSkater == 'C2' or catSkater == 'B1' or catSkater == 'B2' or catSkater == 'A1' or catSkater == 'A2':
            ageCate = 'jr'
        else:
            ageCate = 'sr'

        # dfSBT_nor1 zijn alle results met de jaren los
        dfSBT_nor1 = getSBT(SkaterID, start, end, Distance)

        # Check if there is enough data
        if not dfSBT_nor1.empty and not len(dfSBT_nor1.index) <= 2:

            # All world record years
            seizoenWR = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']

            # World record information
            # Currently hardcoded, would be nice to implement an API connection in the future.
            
            # 1000m
            wrRecords1000ManSR = ['1.07,03', '1.07,00', '1.07,00', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,42', '1.06,18']
            wrRecords1000FemaleSR = ['1.13,11', '1.13,11', '1.13,11', '1.13,11', '1.13,11', '1.13,11', '1.12,68', '1.12,58', '1.12,58', '1.12,18', '1.12,18', '1.12,09', '1.12,09', '1.11,61']
            wrRecords1000ManJR = ['1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,53', '1.08,41', '1.08,11', '1.08,11']
            wrRecords1000FemaleJR = ['1.15,93', '1.15,53', '1.15,41', '1.15,41', '1.15,41', '1.15,41', '1.15,40', '1.14,95', '1.14,95', '1.14,95', '1.14,95', '1.14,95', '1.14,21', '1.14,21']
            dfWR1000ManSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1000ManSR]),  columns=['season', 'record'])
            dfWR1000ManJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1000ManJR]),  columns=['season', 'record'])
            dfWR1000FemaleSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1000FemaleSR]),  columns=['season', 'record'])
            dfWR1000FemaleJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1000FemaleJR]),  columns=['season', 'record'])

            # 1500m
            wrRecords1500ManSR = ['1.42,32', '1.42,01', '1.41,80', '1.41,04', '1.41,04', '1.41,04', '1.41,04', '1.41,04', '1.41,04', '1.41,04', '1.41,04', '1.41,02', '1.41,02', '1.40,17']
            wrRecords1500FemaleSR = ['1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.51,79', '1.50,85', '1.50,85', '1.50,85', '1.50,85', '1.49,83']
            wrRecords1500ManJR = ['1.46,07', '1.45,54', '1.45,54', '1.44,45', '1.44,45	', '1.44,45	', '1.44,45	', '1.44,45	', '1.44,45	', '1.44,45	', '1.44,45	', '1.43.13', '1.43.13', '1.43.13']
            wrRecords1500FemaleJR = ['1.56,69', '1.56,47', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.55,14', '1.54,21', '1.54,21']
            dfWR1500ManSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1500ManSR]),  columns=['season', 'record'])
            dfWR1500ManJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1500ManJR]),  columns=['season', 'record'])
            dfWR1500FemaleSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1500FemaleSR]),  columns=['season', 'record'])
            dfWR1500FemaleJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords1500FemaleJR]),  columns=['season', 'record'])

            # 3000m
            wrRecords3000ManSR = ['3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28', '3.37,28']
            wrRecords3000FemaleSR = ['3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.53,34', '3.52,02']
            wrRecords3000ManJR = ['3.43,20', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.42,98', '3.41,19', '3.40,14', '3.40,14']
            wrRecords3000FemaleJR = ['4.00,63', '4.00,63', '4.00,63', '4.00,63', '4.00,63', '4.00,63', '4.00,63', '4.00,63', '3.59,49', '3.59,49', '3.59,49', '3.59,49', '3.59,47', '3.59,47']
            # Dataframe voor de wereld records op de 1500m
            dfWR3000ManSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords3000ManSR]),  columns=['season', 'record'])
            dfWR3000ManJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords3000ManJR]),  columns=['season', 'record'])
            dfWR3000FemaleSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords3000FemaleSR]),  columns=['season', 'record'])
            dfWR3000FemaleJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords3000FemaleJR]),  columns=['season', 'record'])

            # 5000m
            wrRecords5000ManSR = ['6.08,78', '6.07,48', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86', '6.01,86']
            wrRecords5000FemaleSR = ['6.46,91', '6.45,61', '6.45,61', '6.45,61', '6.45,61', '6.42,66', '6.42,66', '6.42,66', '6.42,66', '6.42,66', '6.42,66', '6.42,66', '6.42,66', '6.42,01']
            wrRecords5000ManJR = ['6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93', '6.18,93']
            wrRecords5000FemaleJR = ['7.09,23', '7.09,23', '7.09,23', '7.09,23', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60', '7.03,60']
            dfWR5000ManSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords5000ManSR]),  columns=['season', 'record'])
            dfWR5000ManJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords5000ManJR]),  columns=['season', 'record'])
            dfWR5000FemaleSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords5000FemaleSR]),  columns=['season', 'record'])
            dfWR5000FemaleJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords5000FemaleJR]),  columns=['season', 'record'])

            # 10000m
            wrRecords10000ManSR = ['12.51,60', '12.41,69', '12.41,69', '12.41,69', '12.41,69', '12.41,69', '12.41,69', '12.41,69', '12.41,69', '12.36,30', '12.36,30', '12.36,30', '12.36,30', '12.36,30']
            wrRecords10000FemaleSR = ['14.08,28', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33', '13.48,33']
            wrRecords10000ManJR = ['13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65', '13.09,65']
            wrRecords10000FemaleJR = ['14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28', '14.08,28']
            dfWR10000ManSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords10000ManSR]),  columns=['season', 'record'])
            dfWR10000ManJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords10000ManJR]),  columns=['season', 'record'])
            dfWR10000FemaleSR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords10000FemaleSR]),  columns=['season', 'record'])
            dfWR10000FemaleJR = pd.DataFrame(np.column_stack([seizoenWR, wrRecords10000FemaleJR]),  columns=['season', 'record'])

            # Set dfWR to the Dataframe that belongs to Distance
            if Distance == 1000:
                if Gender == 'm':
                    if ageCate =='sr':
                        dfWR = dfWR1000ManSR.copy()
                    else:
                        dfWR = dfWR1000ManJR.copy()
                else:
                    if ageCate == 'sr':
                        dfWR = dfWR1000FemaleSR.copy()
                    else:
                        dfWR = dfWR1000FemaleJR.copy()
            elif Distance == 1500:
                if Gender == 'm':
                    if ageCate =='sr':
                        dfWR = dfWR1500ManSR.copy()
                    else:
                        dfWR = dfWR1500ManJR.copy()
                else:
                    if ageCate == 'sr':
                        dfWR = dfWR1500FemaleSR.copy()
                    else:
                        dfWR = dfWR1500FemaleJR.copy()
            elif Distance == 3000:
                if Gender == 'm':
                    if ageCate =='sr':
                        dfWR = dfWR3000ManSR.copy()
                    else:
                        dfWR = dfWR3000ManJR.copy()
                else:
                    if ageCate == 'sr':
                        dfWR = dfWR3000FemaleSR.copy()
                    else:
                        dfWR = dfWR3000FemaleJR.copy()
            elif Distance == 5000:
                if Gender == 'm':
                    if ageCate =='sr':
                        dfWR = dfWR5000ManSR.copy()
                    else:
                        dfWR = dfWR5000ManJR.copy()
                else:
                    if ageCate == 'sr':
                        dfWR = dfWR5000FemaleSR.copy()
                    else:
                        dfWR = dfWR5000FemaleJR.copy()
            elif Distance == 10000:
                if Gender == 'm':
                    if ageCate =='sr':
                        dfWR = dfWR10000ManSR.copy()
                    else:
                        dfWR = dfWR10000ManJR.copy()
                else:
                    if ageCate == 'sr':
                        dfWR = dfWR10000FemaleSR.copy()
                    else:
                        dfWR = dfWR10000FemaleJR.copy()
            else:
                dfWR = dfWR10000FemaleJR

            # New list used to fill a dataframe
            dataSBT = []
            dataWR = []

            # Temporary dataframe that is used later on in order to create a dataframe
            temp = pd.DataFrame(columns=['distance', 'time', 'date', 'location'])

            # Record with all info
            difference = 12
            
            # Skated seasons
            geredenSeizoenen = []

            # A for loop to import API results into a new dataframe
            for i in range(difference):
                try:
                    if not dfSBT_nor1['records'].iloc[i] == []:
                        seizoen = dfSBT_nor1['start'].iloc[i]
                        geredenSeizoenen.append(str(seizoen))

                        temp = pd.json_normalize(dfSBT_nor1.records[i])
                        jaar = dfSBT_nor1['start'].iloc[i]
                        afstand = temp['distance'].iloc[0]

                        tijd = temp['time'].iloc[0]

                        datum = temp['date'].iloc[0]
                        location = temp['location'].iloc[0]

                        # dataWR.append([datum, WR])
                        dataSBT.append([jaar, afstand, tijd, datum, location])
                    # WR = dfWorldRecord['Gereden tijd'].iloc[0]
                except:
                    1+1

            # Fill the new Season bests (SBT) dataframe with data that has been retrieved until now (above)
            dfSBT = pd.DataFrame(data=dataSBT, columns=[
                                'season_year', 'distance', 'time', 'date', 'location'])

            # Limit Dataframe to seasons that were actually skated
            dfWR = dfWR[dfWR['season'].isin(geredenSeizoenen)]
            dfWR = dfWR.reset_index(drop=True)

            # Reversing dfSBT so dfSBT and dfWR are on the same years
            dfSBT = dfSBT.iloc[::-1].reset_index(drop=True)

            # Dataframe combined with WR en SBT
            dfMerged =pd.concat([dfWR, dfSBT['time']], axis=1)

            st.write("Leefdtijdscategorie: " + str(ageCate) +
                "    \nGeslacht: " + str(Gender))

            # Print dataframe
            st.subheader('Season bests van ' + str(chosenSkater) + ':')
            st.write(dfSBT)
            dfMerged['season'] = dfMerged['season'].astype(int)
            # Set figure
            fig = go.Figure()
            
            # SBT
            fig.add_trace(go.Scatter(x=dfMerged['season']-geboorte, y=dfMerged['time'],
                                    mode='lines',
                                    name=str(chosenSkater)))
            # WR
            fig.add_trace(go.Scatter(x=dfMerged['season']-geboorte, y=dfMerged['record'],
                                    mode='lines',
                                    name='WR ' + str(dfWR['record'].iloc[-1])
                                    ))

            # Update figure layout
            fig.update_layout(
                title='Tijd van ' + str(Distance) + 'm',
                xaxis_title="Leeftijd Schaatser",
                yaxis_title="Tijd in minuten",
            )

            # Plotly chart
            #st.subheader('Tijd van '+ str(Distance)+'m')
            st.plotly_chart(fig )

            # A dataframe to calculate rSBT
            dfTemp = dfMerged.copy()

            # Convert SBT to int
            for index, row in dfTemp.iterrows():
                try:
                    if '.' in dfTemp['time'].iloc[index]:
                        x = time.strptime(
                            dfTemp['time'].iloc[index].split(',')[0], '%M.%S')

                        dfTemp['time'].iloc[index] = datetime.timedelta(
                            minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
                    else:
                        dfTemp['time'].iloc[index] = dfTemp['time'].iloc[index].replace(
                            ',', '.')
                except:
                    1+0
            # Convert to int
            dfTemp['time'] = pd.to_numeric(dfTemp['time'])

            # Convert WR to int
            for index, row in dfTemp.iterrows():
                if '.' in dfTemp['record'].iloc[index]:
                    x = time.strptime(
                        dfTemp['record'].iloc[index].split(',')[0], '%M.%S')

                    dfTemp['record'].iloc[index] = datetime.timedelta(
                        minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
                else:
                    dfTemp['record'].iloc[index] = dfTemp['record'].iloc[index].replace(
                        ',', '.')
            # Convert to int
            dfTemp['record'] = pd.to_numeric(dfTemp['record'])
            
            # Empty list which is used later for columns
            rSBTs = []

            # Calculating rSBT and adding it to the list
            for index, row in dfTemp.iterrows():
                rSBT = round((dfTemp['time'].iloc[index] / dfTemp['record'].iloc[index]) * 100, 2)
                
                if rSBT < 100:
                    rSBT = 100
                    # rSBT = 'Nieuw Record'

                rSBTs.append(rSBT)
            
            # Putting rSBTs list into a new dataframe
            dfMerged['percent'] = rSBTs
            
            # Rename columns
            dfMerged = dfMerged.rename(columns={'season': 'Seizoen', 'record': 'Wereld Record*', 'time': str(chosenSkater), 'percent': 'rSBT'})

            # Rows with nan verwijderd
            dfMerged.dropna(subset = ["rSBT"], inplace=True)
            
            # Streamlit print table
            dfMerged['rSBT'] =  dfMerged['rSBT'].astype(str)+ "%"
            st.table(dfMerged.set_index("Seizoen"))  

            # Streamlit print sidenote 
            st.write('*Wereld Record van het begin van het seizoen')

            # Set figure
            fig2 = go.Figure()
            
            # rSBT
            fig2.add_trace(go.Scatter(x=dfMerged['Seizoen'], y=dfMerged['rSBT'],
                                    mode='lines',
                                    name=str(chosenSkater)))

            # Update figure layout
            fig2.update_layout(
                title='Tijd van ' + str(Distance) + 'm',
                xaxis_title="Seizoen",
                yaxis_title="rSBT (%)",
            )

            # Plotly chart
            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.warning("Geen data: Er is geen data gevonden voor " + str(chosenSkater) +
                    " op de " + str(Distance) + "m op speedskatingresults.com")
