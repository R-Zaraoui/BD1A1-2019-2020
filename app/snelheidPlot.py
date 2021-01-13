
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
    import plotly.graph_objects as go

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
        st.error("Fout: Deze schaatser is niet gevonden op speedskatingresults.com")

    else:
        
        # Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatster',skatersFormatted)

        # Getting Skater ID of chosen 
        SkaterID = findSkaterID(chosenSkater,skatersFormatted,skaterListID)

        # URL
        URL = "https://speedskatingresults.com/api/json/skater_results.php"
        
        
        # List that will be filled with distances where there are no data
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
                dfCompetitions.drop(columns=['link'])
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
                dfCompetitions['time'] = pd.to_numeric(dfCompetitions['time'])

                # New empty list to create a new dataframe
                data = []
                
                dfCompetitions['date'] = pd.to_datetime(dfCompetitions['date'])

                # Calculate speed and put into a list
                for index, row in dfCompetitions.iterrows():
                    strindex = str(index + 1)

                    location = dfCompetitions['location'].iloc[index]

                    event = dfCompetitions['name'].iloc[index]

                    date = dfCompetitions['date'].iloc[index]

                    # Extract time variable from the column
                    time = dfCompetitions['time'].iloc[index]

                    # Calculate speed variable to km / h
                    speedEach = (Distance / time) * 3.6

                    # Provide data list with data
                    data.append([strindex, date, speedEach, location, event])

                # Set list to dataframe
                cols = ['id', 'date', 'speed', 'location', 'event']
                dfSpeed = pd.DataFrame(data, columns=cols)
                dfSpeed = dfSpeed.sort_values(by='date')
                dfSpeed = dfSpeed.rename({"speed": "Snelheid"}, axis="columns")
                dfSpeed = dfSpeed.rename({"date": "Datum"}, axis="columns")
                # Calculate average speed from a distance
                avgSpeed = dfSpeed['Snelheid'].mean()
                avgSpeed = "{:.2f}".format(avgSpeed)

                #Plot average speed date
                fig = px.scatter(dfSpeed, x='Datum', y='Snelheid',
                    hover_data={'Snelheid':':.2f',
                    'event':True},
                    hover_name='location'
                )

                dfSpeed['avg'] = avgSpeed

                fig.add_trace(go.Scatter(x=dfSpeed['Datum'], y=dfSpeed['avg'],
                        mode='lines',
                        line=dict(color="red", dash='dot'),
                        name='Gemiddelde snelheid: ' + str(avgSpeed)+" km/u"))

                fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ))
                
                dfTrend = dfSpeed['Snelheid'].copy()
                dfTrend = dfTrend.reset_index(drop=True)

                #Plot average speed index
                fig2 = px.scatter(dfSpeed, x=dfTrend.index, y=dfSpeed['Snelheid'], trendline='lowess', trendline_color_override='red',
                    hover_data={'Snelheid':':.2f',
                    'event':True},
                    hover_name='location')

                fig2.update_layout(
                    xaxis_title="Racenummer",
                    yaxis_title="Gemiddelde Snelheid (km/u)",
                )


                # Update figure layout
                fig.update_layout(
                    #title='Snelheid van ' + str(Distance) + 'm',
                    xaxis_title="Datum",
                    yaxis_title="Gemiddelde Snelheid (km/h)",
                )

                # Plotly chart
                st.subheader('Snelheid van ' + str(Distance) + 'm op datum')
                st.plotly_chart(fig, use_container_width=True)
                st.subheader('Snelheid van ' + str(Distance) + 'm op racenummer')
                st.plotly_chart(fig2,use_container_width=True)

                


            else:
                # Fill emptydistances list with the empty distance
                emptydistances.append(distance)
                if not distances == selectedDistances: 
                    st.error('Er is geen data gevonden voor ' + str(chosenSkater) + ' op de ' + str(Distance) + 'm.')


                # If empty distances all distances contains no notification
                if emptydistances == distances:
                    st.error("GEEN DATA     \n Voeg data toe voor " + str(chosenSkater) +
                            " op speedskatingresults.com om hier een grafiek te plotten")
