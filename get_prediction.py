import pandas as pd
import numpy as np
from flask import Flask, json, request, Response
from sklearn.neural_network import MLPRegressor
from joblib import dump,load


def get_occupancy_prediction(line, modality, day,hour,source,destination,merged_df,cleaned_9292,cleaned_arriva,model):
    if source == destination:
        return {'message': 'error', 'error': 'Source and Destination cannot be the same'}
    if line != '4':
        return {'message': 'error', 'error': 'The MVP supports only line 4 currently'}

    
    #LINE TO SERVE RESULTS FOR, MUST BE MATCHING DATA IN OCCUPANCY DATAFRAMES GIVEN 
    line_names = ['4']

    #ORDER OF STOPS BELOW NEED TO MATCH LINE AND MODALITY GIVEN IN THE PARAMETERS IN THIS CASE: 2
    line_stops = [['Breda, Dreef','Breda, Nieuwe Heilaarstraat','Breda, Woonboulevard','Breda, Liesboslaan','Breda, Ambachtenlaan',
    'Breda, Doelen','Breda, Hovenierstraat','Breda, Burgemeester Sutoriusstraat','Breda, Flierstraat','Breda, Mgr.Nolensplein',
    'Breda, Heuvelbrink','Breda, Dr. Struyckenplein','Breda, Bontekoestraat','Breda, Amphia Zkh. Langendijk',
    'Breda, Langendijk','Breda, Graaf Hendrik III Laan','Breda, Grote Spie','Breda, Irenestraat',
    'Breda, Markendaalseweg','Breda, Centrum','Breda, Vlaszak','Breda, Centraal Station','Breda, Belcrumweg',
    'Breda, Konijnenberg','Breda, Spinveld','Breda, Donk','Breda, Heienlangdonk','Breda, Somerweide','Breda, Noortberghmoeren',
    'Breda, Cannaertserf','Breda, Komoord','Breda, Dwarsdijk','Breda, Emerparklaan','Breda, Heksenwiellaan']]
    
    #CREATE DICTIONARY OF ORDERED STOPS SO THAT WE CAN MATCH GIVEN SOURCE AND DESTINATION
    line_stop_dict = {line_name:line_stop for (line_name,line_stop) in zip(line_names,line_stops)} 
    for key in line_stop_dict.keys():
        line_stop_dict[key] = {stop.lower():num for (num,stop) in enumerate(line_stop_dict[key])}

    #GET NUMBER OF SOURCE AND DESTINATION STOPS GIVEN
    source_num = line_stop_dict[line][source]
    dest_num = line_stop_dict[line][destination]

    #DEPENDING ON THE DIRECTION OF THE REQUESTED TRIP WE SELECT THE CORRESPONDING DATA
    #FOR EXAMPLE FOR source = 2 and destionation = 6 we select stations 2-5 for that day
    if source_num < dest_num:
        res_df = merged_df[(merged_df['Station Num']>=source_num)&(merged_df['Station Num']<dest_num)&(merged_df['Day']==day)]
    if source_num > dest_num:
        res_df = merged_df[(merged_df['Station Num']<=source_num)&(merged_df['Station Num']>dest_num)&(merged_df['Day']==day)]
        

    #9292 request counts for selected stations
    requests_count = np.array([res_df['Occupancy_x'][index] for index in res_df.index]).reshape(-1,1)

    #number of requests happening for that line, day and hour on average
    number_of_requests_hourly = cleaned_9292[(cleaned_9292['Line']==int(line))&(cleaned_9292['Day']==day)&(cleaned_9292['Modaliteitsnummer']==modality)&(cleaned_9292['Hour']==hour)].groupby('Hour').sum()['Count'].mean()
    
    #number of requests happening for that line and day on average
    number_of_requests_daily = cleaned_9292[(cleaned_9292['Line']==int(line))&(cleaned_9292['Day']==day)&(cleaned_9292['Modaliteitsnummer']==modality)].groupby('Hour').sum()['Count'].mean()

    #final result is the prediction of the model multiplied by the percentage of requests that happened in that hour
    result = np.mean(model.predict(requests_count)) * number_of_requests_hourly/number_of_requests_daily
    
    #in case no requests were found in that hour the result of the calclulation will be NaN so we return 0
    if np.isnan(result):
        result = 0

    return {'message': 'success', 'result': result}

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/occupancy-predict', methods=['POST'])
def occupancy_API():

    content = request.get_json()
    #print(content)    

    js_str_ = json.dumps(content)
    params_dict= json.loads(js_str_)


    merged_df = pd.read_pickle('merged_data')
    cleaned_9292 = pd.read_pickle('final_9292')
    cleaned_arriva = pd.read_pickle('final_arriva')
    
    models = load('candidate_models')
    model = models['Tuned MLP']

    line = str(params_dict['line'])
    modality = 2
    hour = int(params_dict['hour'])
    day= str(params_dict['day'])
    source = params_dict['source'].lower()
    destination = params_dict['destination'].lower()
    result = get_occupancy_prediction(line, modality, day, hour,source,destination, merged_df, cleaned_9292,cleaned_arriva, model)
    
    if result['message'] != 'error':
        js_result = json.dumps({'result': result['result']})

        resp = Response(js_result, status=200, mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST'
        resp.headers['Access-Control-Max-Age'] = '1000'
        return resp
    else:
        return json.dumps({'error': result['error']},
                          sort_keys=False, indent=4), 400


app.run(host='0.0.0.0', port=5000)