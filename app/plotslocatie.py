
def runPlot():
    # Imports
    import streamlit as st
    import requests
    import pandas as pd
    import numpy as np
    from pandas.io.json import json_normalize
    import time as timee
    import datetime
    import calendar
    import snelheidPlot
    import plotly.express as px
    from ipywidgets import interactive, HBox, VBox
    import plotly.graph_objs as go
    from scipy import signal
    import math

    # Zet skaterlookup url
    SkaterLookupURL = "https://speedskatingresults.com/api/json/skater_lookup.php"

    # Retrieving skaters by firstname and lastname
    def getSkaters(givenname,familyname):
        parameters = {'givenname':givenname,'familyname':familyname} 
        r = requests.get(url = SkaterLookupURL, params = parameters) 
        data = r.json() 
        results = json_normalize(data)
        resultsNormalized = pd.io.json.json_normalize(results.skaters[0])

        return resultsNormalized

    # Retrieving Skater ID of the chosen skater (in the side menu)
    def findSkaterID(chosenSkater, skatersFormatted,skaterListID):
        search = skatersFormatted.str.find(chosenSkater)
        listIndex = np.where(search == 0)
        skaterID = skaterListID[listIndex[0]]

        return int(skaterID)

    # Sidebar inputs for skaters
    st.sidebar.header("Zoeken:") 
    givenname = st.sidebar.text_input('Voornaam')
    familyname = st.sidebar.text_input('Achternaam')

    # Sidebar inputs for skaters
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
        # Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatster',skatersFormatted)

        # Getting Skater ID of chosen 
        SkaterID = findSkaterID(chosenSkater,skatersFormatted,skaterListID)

        # URL
        URL = "https://speedskatingresults.com/api/json/skater_results.php"
        
        # list that will be filled with distances where there are no data
        emptydistances = []

        # List with all the distances
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

        selectedDistances = []

        selectedDistances = st.sidebar.multiselect('afstanden', distances)

        checkAllDistance = st.sidebar.checkbox('Alle afstanden')

        if checkAllDistance:
            selectedDistances = distances

        # Info
        st.info("Schaatser: " + str(chosenSkater) + "   \nSkaterID: " + str(SkaterID))

        if not selectedDistances:
            st.warning('Geen afstanden geselecteerd')
        else:
            selectedDistances = sorted(selectedDistances)
        
        # For loop to check all the distances
        for distance in selectedDistances:
            Distance = distance
                
            # Get API results
            Parameters = {'skater': SkaterID, 'distance': Distance}
            r = requests.get(url=URL, params=Parameters)
            data = r.json()

            # Json to dataframe
            df = json_normalize(data)

            # Json column to new dataframe
            dfCompetitions = pd.io.json.json_normalize(df.results[0])

            # Check if the dataframe is not empty
            # Else Do not plot
            if not dfCompetitions.empty and not len(dfCompetitions.index) == 1:
                dfCompetitions.drop(columns=['link'])
                dfCompetitions = dfCompetitions.rename({"name": "Event"}, axis="columns")
                dfCompetitions['Racetijd'] = dfCompetitions['time']
                dfCompetitions['Datum'] = ''
                
                #Set time, date column to right format
                for index, row in dfCompetitions.iterrows():
                    dfCompetitions['date'][index] = pd.to_datetime(dfCompetitions['date'][index])
                    dfCompetitions['date'][index] = dfCompetitions['date'][index].strftime('%Y-%m-%d')
                    dfCompetitions['Datum'][index] = pd.to_datetime(dfCompetitions['date'][index]).strftime('%d-%m-%Y')
                    #Split time to minutes and seconds
                    if '.' in dfCompetitions['time'].iloc[index]:
                        x = timee.strptime(
                            dfCompetitions['time'].iloc[index].split(',')[0], '%M.%S')
                        y = dfCompetitions['time'].iloc[index].split(',')[1]

                        dfCompetitions['time'].iloc[index] = datetime.timedelta(
                            minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
                        
                        dfCompetitions['time'][index] = pd.to_numeric(dfCompetitions['time'][index])+float(y)/100.0
                    #Split time to seconds and miliseconds
                    else:
                        x = timee.strptime(dfCompetitions['time'].iloc[index].split(',')[0], '%S')
                        y = dfCompetitions['time'].iloc[index].split(',')[1]

                        dfCompetitions['time'].iloc[index] = datetime.timedelta(
                            seconds=x.tm_sec).total_seconds() 

                        dfCompetitions['time'][index] = pd.to_numeric(dfCompetitions['time'][index])+float(y)/100.0  
                # Convert to int
                
                data = []

                dfCompetitions = dfCompetitions.sort_values(by='location')
                dfCompetitions = dfCompetitions.rename({"location": "Locatie"}, axis="columns")
                dfCompetitions = dfCompetitions.rename({"date": "Datum2"}, axis="columns")
                dfCompetitions = dfCompetitions.rename({"time": "Time"}, axis="columns")

                # Set figure
                fig = px.scatter(dfCompetitions, x="Datum2", y="Time", color='Locatie',hover_name='Locatie', hover_data={'Datum2':False,'Datum':True,'Racetijd':True,'Time':False,'Event':True})

                # Update figure layout
                fig.update_layout(
                    title='Tijden op de ' + str(Distance) + 'm',
                    xaxis_title="Datum",
                    yaxis_title="Tijd (s)",
                    height=400,\
                )

                dfCompetitions = dfCompetitions.sort_values(by='Datum2')
                for index in range(len(dfCompetitions)):
                    dfCompetitions['Datum'][index] = pd.to_datetime(dfCompetitions['Datum'][index])
                    dfCompetitions['Datum'][index] = dfCompetitions['Datum'][index].strftime('%d-%m-%Y')
                dfTrend = dfCompetitions[['Time','Locatie','Event','Racetijd','Datum']].copy()
                dfTrend = dfTrend.reset_index(drop=True)
                dfTrend['Racenummer'] = dfTrend.index + 1

                #Round y as to nearest multiple of 5 seconds.
                maxround = 5 * math.ceil(max(dfTrend['Time'] / 5.0))
                minround = 5 * math.floor(min(dfTrend['Time'] / 5.0))

                #Create string arrays containing proper time format (MM:ss:mm)
                if maxround - minround > 10:
                    y_array2 = [i for i in range(minround, maxround, 5)]
                    y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround, maxround, 5)]
                else:
                    y_array2 = [i for i in range(minround, maxround, 1)]
                    y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround, maxround, 1)]

                fig2 = px.scatter(dfTrend, x='Racenummer', y='Time',hover_name='Locatie', hover_data={'Datum':True,'Racenummer':True,'Racetijd':True,'Time':False,'Event':True})

                
                if len(dfTrend)%2 == 0:
                    lendf = len(dfTrend)-1
                else:
                    lendf = len(dfTrend)
                fig2.update_layout(
                    title='Trend van ' + str(Distance) + 'm',
                    xaxis_title="Race nummer",
                    yaxis_title="Tijd (s)",
                )

                fig2.update_layout(yaxis=dict(tickmode='array', tickvals=y_array2, ticktext=y_array1))
                fig.update_layout(yaxis=dict(tickmode='array', tickvals=y_array2, ticktext=y_array1))
                
                #Savitzky–Golay fitted (trend) line
                if len(dfTrend) > 9:
                    fig2.add_trace(
                        go.Scatter(
                        x=dfTrend['Racenummer'],
                        y=signal.savgol_filter(dfTrend['Time'], lendf, 3),
                        mode='lines',
                        name='Trendlijn'
                        )
                    )
                
                # Plotly chart
                st.plotly_chart(fig, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)

                # Print long solid line to see distances split easier
                slashes = '-' * 30
                st.write(slashes)

            else:
                # Fill emptydistances list with the empty distance
                if dfCompetitions.empty:
                    st.error('Er is geen data gevonden voor ' + str(chosenSkater) + ' op de ' + str(Distance) + 'm.')
                    st.error('Er is geen data gevonden voor'+'      '+'....'+'      '+'op de'+'      '+'....'+'      '+'m.')
                emptydistances.append(distance)
                if not distances == selectedDistances: 
                    st.warning('Er is geen data gevonden voor ' + str(chosenSkater) + ' op de ' + str(Distance) + 'm.')

                # If empty distances all distances contains no notification
                if emptydistances == distances:
                    st.error("GEEN DATA     \n Voeg data toe voor " + str(chosenSkater) +
                            " op speedskatingresults.com om hier een grafiek te plotten")
