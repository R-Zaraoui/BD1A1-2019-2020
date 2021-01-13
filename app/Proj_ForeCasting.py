def runPlot():
    import streamlit as st
    import numpy as np
    import requests 
    import pandas as pd
    from pandas.io.json import json_normalize
    import time as timee
    import datetime
    import calendar
    import plotly.graph_objs as go
    import plotly.express as px


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

    # Sidebar inputs for skaters
    st.sidebar.header("Zoeken:") 
    givenname = st.sidebar.text_input('Voornaam')
    familyname = st.sidebar.text_input('Achternaam')

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

    selectedDistances = st.sidebar.multiselect('Afstanden', distances)
    
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
        st.error("Fout: Deze schaatser is niet gevonden op speedskatingresults.com")
    else:

        #Sidebar dropdown menu with a list of skaters (results of search query)
        chosenSkater = st.sidebar.selectbox('Schaatser',skatersFormatted)

        #Getting Skater ID of chosen skater
        SkaterID = findSkaterID(chosenSkater,skatersFormatted,skaterListID)
        
        for distance in selectedDistances:
            Distance = distance

            # Retrieving data using API
            Parameters = {'skater': SkaterID, 'distance': Distance}
            r = requests.get(url=URL, params=Parameters)
            data = r.json()

            # Json to dataframe
            df = json_normalize(data)

            # Json column to new dataframe
            dfCompetitions = pd.io.json.json_normalize(df.results[0])
            dfCompetitions['Datum'] = ''
            if not dfCompetitions.empty and not len(dfCompetitions.index) == 1:
                for index, row in dfCompetitions.iterrows():
                            #dfCompetitions['date'][index] = dfCompetitions['date'].iloc[index].split('T')[0]
                            dfCompetitions['date'][index] = pd.to_datetime(dfCompetitions['date'][index])
                            dfCompetitions['date'][index] = dfCompetitions['date'][index].strftime('%Y-%m-%d')
                            dfCompetitions['Datum'][index] = pd.to_datetime(dfCompetitions['date'][index]).strftime('%d-%m-%Y')
                            if '.' in dfCompetitions['time'].iloc[index]:
                                x = timee.strptime(
                                    dfCompetitions['time'].iloc[index].split(',')[0], '%M.%S')
                                y = dfCompetitions['time'].iloc[index].split(',')[1]

                                dfCompetitions['time'].iloc[index] = datetime.timedelta(
                                    minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
                                
                                dfCompetitions['time'][index] = pd.to_numeric(dfCompetitions['time'][index])+float(y)/100.0
                            else:
                                #dfCompetitions['time'].iloc[index] = dfCompetitions['time'].iloc[index].replace(',', '.')
                                x = timee.strptime(dfCompetitions['time'].iloc[index].split(',')[0], '%S')
                                y = dfCompetitions['time'].iloc[index].split(',')[1]

                                dfCompetitions['time'].iloc[index] = datetime.timedelta(
                                    seconds=x.tm_sec).total_seconds() 

                                dfCompetitions['time'][index] = pd.to_numeric(dfCompetitions['time'][index])+float(y)/100.0               
                import matplotlib.pyplot as plt
                import pandas 
                import math
                from keras.models import Sequential
                from keras.layers import Dense
                from keras.layers import LSTM
                from sklearn.preprocessing import MinMaxScaler
                from sklearn.metrics import mean_squared_error
                import numpy

                
                df = dfCompetitions
                #Check if predictions are possible
                if len(df) > 90:
                    with st.spinner('Even geduld, voorspellingen worden berekend.'):
                        timee.sleep(5)
                    df = df.sort_values('date').reset_index(drop=False)
                    df2 = df.sort_values('date').reset_index(drop=False)
                    df['res'] = ''
                    df['multi'] = ''
                    df['upper'] = ''
                    df['lower'] = ''
                    df['upper5'] = ''
                    df['lower5'] = ''

                    for i in range(1,2):
                        look_back=15
                        dataframe = pandas.DataFrame(df["time"])
                        dataset = dataframe.values
                        datasetplot  = dataframe.values
                        dataset = dataset.astype('float32')

                        scaler = MinMaxScaler(feature_range=(0, 1))
                        dataset = scaler.fit_transform(dataset)
                        #normalize
                        train_size = int(len(dataset) * 0.80)
                        test_size = len(dataset) - train_size
                        train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
                        #Convert array to matrix
                        def create_dataset(dataset, look_back=1):
                            dataX, dataY = [], []
                            for i in range(len(dataset)-look_back-1):
                                a = dataset[i:(i+look_back), 0]
                                dataX.append(a)
                                dataY.append(dataset[i + look_back, 0])
                            return numpy.array(dataX), numpy.array(dataY)
                        #Split train,test
                        trainX, trainY = create_dataset(train, look_back)
                        testX, testY = create_dataset(test, look_back)
                        trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
                        testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

                        # create and fit the LSTM network
                        model = Sequential()
                        model.add(LSTM(4, input_shape=(1, look_back)))
                        model.add(Dense(1))
                        model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
                        history = model.fit(trainX, trainY, epochs=30, batch_size=1, verbose=1)
                        # make predictions
                        trainPredict = model.predict(trainX)
                        testPredict = model.predict(testX)
                        # invert predictions
                        trainPredict = scaler.inverse_transform(trainPredict)
                        trainY = scaler.inverse_transform([trainY])
                        testPredict = scaler.inverse_transform(testPredict)
                        testY = scaler.inverse_transform([testY])
                        # calculate root mean squared error
                        trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
                        testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
                        # shift train predictions for plotting
                        trainPredictPlot = numpy.empty_like(dataset)
                        trainPredictPlot[:, :] = numpy.nan
                        trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
                        # shift test predictions for plotting
                        testPredictPlot = numpy.empty_like(dataset)
                        testPredictPlot[:, :] = numpy.nan
                        testPredictPlot[len(trainPredict)+(2*look_back)+2:len(dataset)] = testPredict

                        #Add prediction to time columns
                        dfdf = pandas.DataFrame(testPredictPlot)
                        df = pandas.concat([df,dfdf[-1:]], ignore_index=True)
                        df['pred'] = df[0]
                        df['time'][-1:] = df['pred'][-1:]
                        #Calculate residuals
                        for k in range(look_back, len(trainPredict)+look_back):
                            df['res'][k] = trainPredictPlot[k]-df['time'][k]

                        #Calculate 15 forward prediction
                        for j in range(1,15):
                            dataframe = pandas.DataFrame(df["time"])
                            dataset = dataframe.values
                            datasetplot  = dataframe.values
                            dataset = dataset.astype('float32')
                            
                            scaler = MinMaxScaler(feature_range=(0, 1))
                            dataset = scaler.fit_transform(dataset)

                            test = dataset[30:len(dataset),:]
                            testX, testY = create_dataset(test, look_back)
                            testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

                            testPredict = model.predict(testX)
                            testPredict = scaler.inverse_transform(testPredict)
                            testY = scaler.inverse_transform([testY])

                            testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))

                            testPredictPlot = numpy.empty_like(dataset)
                            testPredictPlot[:, :] = numpy.nan
                            testPredictPlot[16+(2*look_back):len(dataset)] = testPredict

                            dfdf = pandas.DataFrame(testPredictPlot)
                            df = pandas.concat([df,dfdf[-1:]], ignore_index=True)
                            
                            df['pred'] = df[0]
                            df['time'][-1:] = df['pred'][-1:]

                    #calculate MSE for each ith prediction
                    for i in range(1,len(df)):
                        if i < len(df)-15:
                            df.multi[i] = 0
                        else:
                            df.multi[i] = math.sqrt(i-len(df)+16)*df['res'][15:71].std()

                    #Set upper/lower bounds for the prediction interval
                    for i in range(len(df)):
                        if i < len(df)-16:
                            df['upper'][i]=numpy.nan
                            df['lower'][i]=numpy.nan
                            df['upper5'][i]=numpy.nan
                            df['lower5'][i]=numpy.nan
                        else:
                            df['upper'][i] = df['time'][i] + 1.28*df.multi[i]
                            df['lower'][i] = df['time'][i] - 1.28*df.multi[i]
                            df['upper5'][i] = df['time'][i] + 0.67*df.multi[i]
                            df['lower5'][i] = df['time'][i] - 0.67*df.multi[i]
                    array_upper = pandas.to_numeric(pandas.Series(df['upper']))
                    array_lower = pandas.to_numeric(pandas.Series(df['lower']))
                    array_upper5 = pandas.to_numeric(pandas.Series(df['upper5']))
                    array_lower5 = pandas.to_numeric(pandas.Series(df['lower5']))

                    maxround = 5 * math.ceil(max(df['time'] / 5.0))
                    minround = 5 * math.floor(min(df['time'] / 5.0))
                    #Set proper y-axis interval
                    if maxround - minround > 10:
                        y_array2 = [i for i in range(minround-10, maxround, 5)]
                        y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround-10, maxround, 5)]
                    else:
                        y_array2 = [i for i in range(minround, maxround, 1)]
                        y_array1 = [str(t//60)+'.'+'%02d'%(t-((t//60)*60))+',00' for t in range(minround, maxround, 1)]

                    #Check if mean residuals are 0 (assumption residuals ~ normal distribution)
                    if abs(1.68*df['res'][15:71].std()) > abs(df['res'][15:71].mean()):
                        #Plot figure and prediction line
                        fig = go.Figure()
                        fig = px.line(df, x=df.index, y=df.time,
                                title="",
                                labels={'x':'x','y':'y'})
                        fig.update_traces(line_color='orange')
                        fig.update_layout(
                        xaxis_title="Race nummer",
                        yaxis_title="Tijd (m.s,ms)")

                        fig.update_layout(yaxis=dict(tickmode='array', tickvals=y_array2, ticktext=y_array1))
                        #plot and fill predicion intervals
                        fig.add_trace(go.Scatter(x=df.index, y=array_lower, 
                                                                        mode = 'lines', 
                                                                        line_color = 'dimgray',
                                                                        name='80% CI Ondergrens',
                                                                        legendgroup='Test',
                                                                        showlegend=False))
                                                                        
                        fig.add_trace(go.Scatter(x=df.index, y=array_upper, 
                                                                        fill = 'tonexty', 
                                                                        mode = 'lines', 
                                                                        line_color = 'dimgray',
                                                                        name='80% Prediction interval'))
                        
                        fig.add_trace(go.Scatter(x=df.index, y=array_lower5, 
                                                                        mode = 'lines', 
                                                                        line_color = 'dimgray',
                                                                        name='50% Prediction interval'))
                                                                        
                        fig.add_trace(go.Scatter(x=df.index, y=array_upper5, 
                                                                        fill = 'tonexty', 
                                                                        mode = 'lines', 
                                                                        line_color = 'dimgray',
                                                                        name='50% CI Bovengrens',
                                                                        legendgroup='Test',
                                                                        showlegend=False))
                        
                        fig.add_trace(go.Scatter(x=df.index, y=df.time, 
                                                                        mode = 'lines', 
                                                                        line_color = 'blue',
                                                                        name='Voorspelling'))

                        fig.add_trace(go.Scatter(x=df2.index, y=df2.time, 
                                                                        mode = 'lines', 
                                                                        line_color = '#FFA15A',
                                                                        name='Originele data',
                                                                        legendgroup='Test',
                                                                        showlegend=False))

                        st.subheader('Voorspelling van ' + str(Distance) + 'm')
                        #Plot figure
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error('Time series forecasting niet mogelijk omdat '+str(df['res'][15:71].mean())+' te ver van 0 is')
                else:
                    st.error('Het voorspellen van de ' +str(Distance)+ 'm is niet mogelijk, omdat er onvoldoende datapunten zijn')

            else:
                    st.error('Het voorspellen van de ' +str(Distance)+ 'm is niet mogelijk, omdat er geen datapunten zijn')
                    
                    
