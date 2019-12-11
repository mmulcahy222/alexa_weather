import urllib2
import json
import re

def lambda_handler(event, context):
    try:
        if (event["session"]["application"]["applicationId"] != "amzn1.ask.skill.f666833d-0180-4411-a3d3-b81ead968f33"):
            raise ValueError("Invalid Application ID")
        if event["session"]["new"]:
            print "Starting new session."
        if event["request"]["type"] == "LaunchRequest":
            #this is what really runs
            return build_response(get_weather(), 1)
        elif event["request"]["type"] == "IntentRequest": 
            intent_name = event["request"]["intent"]["name"]
            if intent_name == "GetWeather":
                return build_response(get_weather(), 1)
            elif intent_name == "AMAZON.HelpIntent":
                return build_response('You Want Help', 1)
            elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
                 return build_response('Thank you for using Goon. See you next time!', true)
            else:
                raise ValueError("Invalid intent")
        elif event["request"]["type"] == "SessionEndedRequest":
            return on_session_ended(event["request"], event["session"])
    except Exception as e:
        return build_response(e, 1)

def get_weather():
    #read from file
    #testing
    w_dict = json.loads(urllib2.urlopen('http://api.wunderground.com/api//forecast/geolookup/conditions/q/NY/New_Paltz.json').read().replace('\n','').replace('\t','').strip())
    #read from file
    #w_dict = json.loads(urllib2.urlopen('http://api.wunderground.com/api//forecast/geolookup/conditions/q/CA/San_Francisco.json').read().replace('\n','').replace('\t','').strip())
    response = '<speak>'
    text_forecast = w_dict['forecast']['txt_forecast']['forecastday']
    number_forecast = w_dict['forecast']['simpleforecast']['forecastday']
    current_observation = w_dict['current_observation']
    #weekday
    for node in number_forecast:
        day = node['date']['weekday']
        qpf_day = node['qpf_day']['in']
        qpf_night = node['qpf_night']['in']
        snow_day = node['snow_day']['in']
        snow_night = node['snow_night']['in']
        if snow_day != 0 and snow_day is not None:
            response += "In the daytime of %s, snow is %s inches.  <break time='4000ms'/> " % (day, snow_day)
        if snow_night != 0 and snow_night is not None:
            response += "In the night hours of %s, snow is %s inches. <break time='4000ms'/> " % (day, snow_night)
        if qpf_day != 0 and qpf_day is not None:
            response += "In the daytime of %s, precipitation is %s inches. <break time='4000ms'/> " % (day, qpf_day)
        if qpf_night != 0 and qpf_night is not None:
            response +=  "In the night hours of %s, precipitation is %s inches. <break time='4000ms'/> " % (day, qpf_night)
    regular_list = []
    response += ' The full forecast is '
    for node in text_forecast:
        response += 'On ' + node['title'] + ', the weather will be ' + re.sub(r'(\d{2,3})[F|f]\.? ','\\1 degrees ',node['fcttext']) + " <break time='4000ms'/>  "
    response += '</speak>'
    return response

def build_response(speech_output, should_end_session):
    return {
    
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": speech_output
            }, 
            "shouldEndSession": should_end_session
            # "card": {
            #     "type": "Simple",
            #     "title": title,
            #     "content": output
            # },
            # "reprompt": {
            #     "outputSpeech": {
            #         "type": "PlainText",
            #         "text": reprompt_text
            #     }
            # },
        }
    }