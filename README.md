# DEIA I project, Group 9

# In collaboration with Smartwayz


# In this repository a notebook is included with the steps we followed to process 
# the data as well as all of the dataframes produced and required for the code to execute.


# get_prediction.py is a simple Flask API that when executed can serve requests for occupancy predictions 
# on bus line 4 of Breda.

# the API runs at the link: http://<your-external-ip>:5000/occupancy-predict
# and receives POST HTTP requests with the parameters in the body. An example set of valid parameters is as shown: 

# {
# 	"line": "4",
#	"hour": 2,
#	"day": "Monday",
#	"source": "Breda, Dr. Struyckenplein",
#	"destination": "Breda, Belcrumweg"
# }

# In order to modify the API to serve predictions for a different line new occupancy and merge dataframes need to be 
# created using the functions in the notebook by using a correct ordered list of stations for that line (and modality number)

# You can verify that your list matches the data by checking the station names in the final_9292 and final_arriva datasets 
# for that line and modality number.