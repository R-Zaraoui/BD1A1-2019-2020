
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
    import plotly.graph_objs as go
    from scipy import signal
    import math

    # API source
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

    # Retrieving skaters with user input
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

        # Info
        st.info("Schaatser: " + str(chosenSkater) + "   \nSkaterID: " + str(SkaterID))

        selectedDistances = []

        selectedDistances = st.sidebar.multiselect('afstanden', distances)

        checkAllDistance = st.sidebar.checkbox('Alle afstanden')

        if checkAllDistance:
            selectedDistances = distances

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

            # Else Do not plot
            if not dfCompetitions.empty and not len(dfCompetitions.index) == 1:
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

                #Rename some columns
                dfCompetitions = dfCompetitions.sort_values(by='date')
                dfCompetitions = dfCompetitions.rename({"location": "Locatie"}, axis="columns")
                dfCompetitions = dfCompetitions.rename({"date": "Datum2"}, axis="columns")
                dfCompetitions = dfCompetitions.rename({"time": "Time"}, axis="columns")
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

                # Set figure
                fig = px.scatter(dfCompetitions, x="Datum2", y="Time", color='Soort evenement',hover_name='Event', hover_data={'Datum2':False,'Datum':True,'Racetijd':True,'Time':False,'Event':True},
                        category_orders={'Soort evenement':['Olympische Wedstrijden','Wereld Kampioenschappen', 'Europese Kampioenschappen', 'Nationale Kampioenschappen', 'Wereld Cup', 'Overige Evenementen']})


                # Update figure layout
                fig.update_layout(
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

                maxround = 5 * math.ceil(max(dfTrend['Time'] / 5.0))
                minround = 5 * math.floor(min(dfTrend['Time'] / 5.0))

                #Create string arrays containing proper time format (MM:ss:mm)
                if maxround - minround > 10:
                    y_array2 = [i for i in range(minround, maxround, 5)]
                    y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround, maxround, 5)]
                else:
                    y_array2 = [i for i in range(minround, maxround, 1)]
                    y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround, maxround, 1)]

                #plot second figure
                fig2 = px.scatter(dfTrend, x='Racenummer', y='Time', hover_name='Locatie', hover_data={'Datum':False,'Datum':True,'Racetijd':True,'Time':False,'Event':True})

                fig2.update_layout(
                    xaxis_title="Racenummer",
                    yaxis_title="Tijd (m.s,ms)",
                )
                fig2.update_layout(yaxis=dict(tickmode='array', tickvals=y_array2, ticktext=y_array1))
                fig.update_layout(yaxis=dict(tickmode='array', tickvals=y_array2, ticktext=y_array1))

                if len(dfCompetitions)%2 == 0:
                    lendf = len(dfCompetitions)-1
                else:
                    lendf = len(dfCompetitions)

                #Savitzky–Golay fitted (trend) line of degree 6
                if len(dfTrend) > 9:
                    fig2.add_trace(
                        go.Scatter(
                        x=dfTrend.index,
                        y=signal.savgol_filter(dfCompetitions['Time'], lendf, 6),
                        mode='lines',
                        name='Trendlijn'
                        )
                    )

                # Plotly chart
                st.subheader('Plot afstanden op locatie ' + str(Distance) + 'm')
                st.plotly_chart(fig, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)


            else:
                if dfCompetitions.empty:
                    st.error('Er is geen data gevonden voor ' + str(chosenSkater) + ' op de ' + str(Distance) + 'm.')
                # Fill emptydistances list with the empty distance
                emptydistances.append(distance)
                if not distances == selectedDistances: 
                    st.warning('Er is geen data gevonden voor ' + str(chosenSkater) + ' op de ' + str(Distance) + 'm.')

                # If empty distances all distances contains no notification
                if emptydistances == distances:
                    st.error("GEEN DATA     \n Voeg data toe voor " + str(chosenSkater) +
                            " op speedskatingresults.com om hier een grafiek te plotten")
