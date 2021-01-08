# Imports
import streamlit as st
import snelheidPlot
import AlleDataPlot
import personal_records
import plotslocatie
import performanceTracker
import EvenementPlot
import home
import Proj_ForeCasting
from PIL import Image

#Main CSS markup on top of Streamlit for the KNSB theme
html = """
<style>

.sidebar .sidebar-content {
  background-color: #F39D12;
  background-image: none;
  color: white;
}

.sidebar img{
    margin-top: -35px;  
}

.stTextInput label{
    color:white;
}
.stSelectbox label{
    color:white;
}

.stRadio label{
    color:white;
}
.stMultiSelect label{
    color:white;
}
.logo{
    width:250px;
}
.knsb{
    width:100px;
    display: inline-block;
    padding:10px;
  opacity: 1;


    z-index:5;
}
.hva{
    width:135px;
    display: inline-block;
    padding:10px;
  opacity: 1;


    z-index:5;
}
.datavalley{
    width:100px;
    display: inline-block;
    padding:10px;
  opacity: 1;

    z-index:5;
}
.sidebar{

}
footer{
    text-align:center;
}

</style>
"""
speedskatinglogo = "<img class=\"logo\" src=\"https://i.imgur.com/aF1Lgnx.png\" />"
logos = """

<footer><img class="knsb" src=\"https://i.imgur.com/VSveX8J.png\" /> 
<img class="hva" src=\"https://i.imgur.com/JMyruEu.png\" /> 
<img class="datavalley" src=\"https://i.imgur.com/gysnqiq.png\" /> </footer>

"""


st.markdown(html, unsafe_allow_html=True)
st.sidebar.markdown(speedskatinglogo, unsafe_allow_html=True)

# Dropdown with choices to select a plot
plots = ['Home','Gemiddelde snelheid', 'Persoonlijke Records','Locatie plot', 'Evenement Plot', 'Voorspelling Plot', 'Alle Data']
plotTab = st.sidebar.selectbox('Selecteer een Plot', plots)



# Calling plots chosen by user input
if plotTab == 'Home': #default
    home.runPlot()
elif plotTab == 'Performance Tracker': #performanceTracker
    st.title('Performance tracker')
    performanceTracker.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Gemiddelde snelheid': #snelheidPlot
    st.title("Gemiddelde snelheid van alle seizoenen")
    snelheidPlot.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Persoonlijke Records': #personal_records
    personal_records.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Locatie plot': #plotslocatie
    st.title('Locatie plot')
    plotslocatie.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Alle Data': #dataframePlot
    st.title('Alle data')
    AlleDataPlot.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Evenement Plot': #Evenement Plot
    st.title('Evenement Plot')
    EvenementPlot.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

elif plotTab == 'Voorspelling Plot': #Voorspelling Plot
    st.title('Voorspelling Plot')
    Proj_ForeCasting.runPlot()
    st.markdown(logos, unsafe_allow_html=True)

else: #Error
    st.error("Geen keuze gemaakt in het menu")
