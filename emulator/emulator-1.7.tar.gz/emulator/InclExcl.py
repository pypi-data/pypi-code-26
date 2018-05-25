#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 16:10:55 2018

@author: ashraya
"""

import os
import json, time, uuid

log_file = "log.log"

DEBUG = True

def Log(log):
    if (DEBUG == True):
        with open(log_file, "a") as logFp:
            logFp.write(log + "\n")

def serv_topic(service, address, resource_name):
    return "/rt:dev/rn:{}/ad:1/sv:{}/ad:{}_0".format(resource_name, service, address)

def get_services(name):
    switch = { "red" : "color_ctrl", "blue" : "color_ctrl", "green" : "color_ctrl", "kWh" : "meter_elec", "W" : "meter_elec", "A" : "meter_elec", "V" : "meter_elec"}
    
    plug = {}
    
    light = {"warm_w" : "color_ctrl", "cold_w" : "color_ctrl", "red" : "color_ctrl", "blue" : "color_ctrl", "green" : "color_ctrl"}
    
    thermostat = {}
    
    motion = {}
    
    multi = {"temper_removed_cover" : "alarm_burglar", "C" : "sensor_temp", "F" : "sensor_temp", "Lux" : "sensor_lumin", "%" : "sensor_humid", "index" : "sensor_uv"}
    
    dimmer = {"overheat" : "alarm_heat", "surge" : "alarm_power", "voltage_drop" : "alarm_power", "over_current" : "alarm_power", "load_error" : "alarm_power", 
              "hw_failure" : "alarm_system", "W" : "sensor_power"}
    
    flood = {"leak" : "alarm_water", "gp" : "alarm_gp", "C" : "sensor_temp"}
    
    window = {}
    
    door = {"rf_not_locked" : "alarm_lock"}

    alarm = {"temper_removed_cover" : "alarm_burglar", "ac_on" : "alarm_power", "ac_off" : "alarm_power", "overheat" : "alarm_heat", "CO" : "alarm_gas",
             "smoke" : "alarm_fire", "smoke_test" : "alarm_fire"}    

    serv_dict = { "switch" : switch ,
                  "plug" : plug ,
                  "light" : light ,
                  "thermostat" : thermostat ,
                  "alarm" : alarm ,
                  "motion" : motion ,
                  "multi" : multi ,
                  "dimmer" : dimmer ,
                  "flood" : flood ,
                  "window" : window ,
                  "door" : door }
    
    return serv_dict[name]

def get_device_params(name):
    service_dict = {
        "switch" : { "on" : {   "evt.binary.report" : "out_bin_switch"  },  
                     "off" : {  "cmd.binary.set" : "out_bin_switch" },
                     "level" : {    "evt.lvl.report" : "out_lvl_switch",
                                    "cmd.lvl.set" : "out_lvl_switch",
                                    "cmd.lvl.start" : "out_lvl_switch",
                                    "cmd.lvl.stop" : "out_lvl_switch",
                                    "cmd.binary.set" :  "out_lvl_switch",
                                    "evt.binary.report" : "out_lvl_switch" }
                   },  
        "alarm" : { 
                     "on" : {    "evt.alarm.report" : "alarm_fire"  },  
                     "off" : {   "evt.alarm.report" : "alarm_fire"  },  
                     "battery" : {  "evt.lvl.report" : "battery",
                                    "evt.alarm.report" : "battery" }
                  },  
        "dimmer" : { 
                     "on" : {   "evt.binary.report" : "out_lvl_switch"  },  
                     "off" : {  "cmd.binary.set" : "out_lvl_switch" },
                     "level" : {    "evt.lvl.report" : "out_lvl_switch",
                                    "cmd.lvl.set" : "out_lvl_switch",
                                    "cmd.lvl.start" : "out_lvl_switch",
                                    "cmd.lvl.stop" : "out_lvl_switch",
                                    "cmd.binary.set" :  "out_lvl_switch",
                                    "evt.binary.report" : "out_lvl_switch"  }
                   },  
        "door" : { 
                     "sensor" : {   "evt.presence.report" : "sensor_presence" },
                     "on" : {   "evt.lock.report" : "door_lock" },
                     "off" : {  "cmd.lock.set" : "door_lock"    },  
                     "battery" : {  "evt.lvl.report" : "battery",
                                    "evt.alarm.report" : "battery" }
                 },  
        "flood" : { 
                     "on" : {   "evt.alarm.report" : "alarm_water"  },  
                     "off" : {  "evt.alarm.report" : "alarm_water" },
                     "battery" : {  "evt.lvl.report" : "battery",
                                    "evt.alarm.report" : "battery"  }
                  },  
        "light" : { 
                     "on" : {   "evt.binary.report" : "out_lvl_switch"  },  
                     "off" : {  "cmd.binary.set" : "out_lvl_switch" },
                     "set"  :   {   "cmd.scene.set" : "scene_ctrl"  },  
                     "level" : {    "evt.lvl.report" : "out_lvl_switch",
                                    "cmd.lvl.set" : "out_lvl_switch",
                                    "cmd.lvl.start" : "out_lvl_switch",
                                    "cmd.lvl.stop" : "out_lvl_switch",
                                    "cmd.binary.set" :  "out_lvl_switch",
                                    "evt.binary.report" : "out_lvl_switch"  }
                  },  
        "multi" : { 
                     "on" : {   "evt.alarm.report" : "alarm_burglar"  },  
                     "off" : {  "evt.alarm.report" : "alarm_burglar" },
                     "sensor" : {   "evt_presence_report" : "sensor_presence" },
                     "battery" : {  "evt.lvl.report" : "battery",
                                    "evt.alarm.report" : "battery"  }                                                                                                                                                                                                              
                  } 
    }

    return service_dict[name]

def dump_inclusion_report(services, name, req, address="1", service="emul-def"):
    Log("dump_inclusion_report" + str(req))
    service_str = []
    for item in services:
        topic = serv_topic(item, address, service)
        service_dict = \
        {
            "address": topic,
            "enabled": True,
            "groups": [
                "ch_0"
            ],
            "interfaces": [
                {
                    "intf_t": "out",
                    "msg_t": "evt." + name + ".report",
                    "val_t": "str_map",
                    "ver": "1"
                },
                {
                    "intf_t": "in",
                    "msg_t": "cmd." + name + ".get_report",
                    "val_t": "string",
                    "ver": "1"
                }
            ],
            "location": "",
            "name": item,
            "prop_set_ref": "nif_0",
            "props": {
            "is_secure": True,
            "is_unsecure": False,
            "sup_events": services[item]
            }
        }
        
        service_str.append(service_dict)
    
        Log("dump_inclusion_report: service_str : " + str(service_str))
        Log("dump_inclusion_report: req['device_id']" + str(req['device_id']))
    
    return \
    {
        "ctime": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "props": {},
        "serv": "emul",
        "tags": [],
        "type": "evt.thing.inclusion_report",
        "val": {
            "address": address,
            "category": "UNKNOWN ",
            "comm_tech": "emul",
            "device_id": req['device_id'],
            "groups": [
                "ch_0"
            ],
            "hw_ver": req["hw_ver"],
            "is_sensor": "0",
            "manufacturer_id": req["manufacturer_id"],
            "power_source": req["power_source"],
            "product_hash": req["product_hash"],
            "product_id": req["product_id"],
            "product_name": req["product_name"],
            "prop_set": {},
            "security": "secure_S2",
            "services": service_str,
            "sw_ver": "1",
            "tech_specific_props": {},
            "wakeup_interval": req["wakeup_interval"]
        },
        "val_t": "object",
        "ver": 1,
        "uid": str(uuid.uuid4())
    }
      
def dump_exclusion_report(address="1", service=""):
  return \
    {
      "type": "evt.thing.exclusion_report",
      "serv": service,
      "val_t": "object",
      "val":{"address": str(address)},
      "tags": [],
      "props": {},
      "ctime": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
      "ver": "1",
      "uid": str(uuid.uuid4())
    }
        
def dump_trigger_report(device, address, event, status, service):
    svcs_dict = get_services(device)          
    value = svcs_dict[event]
    topic = "pt:j1/mt:evt/rt:dev/rn:{}/ad:1/sv:{}/ad:{}_0".format("emul", value, address)
    
    st = ""
    if (status == True):
        st = "activ"
    else:
        st = "inactiv"
        
    return \
      topic, {
        "ctime": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "props": {},
        "serv": value,
        "tags": [],
        "type": "evt."+value+".report",
        "val": {
          "event": value,
          "status": st
        },
        "val_t": "str_map",
        "ver": 1,
        "uid": str(uuid.uuid4())
    }    

def value_on_switch(name, status):
    val_dict = get_device_params(name)
    if status == True:
        return val_dict["on"]
    elif status == False:
        return val_dict["off"]
    else:
        return val_dict["level"]

def value_on_dimmer_alarm_flood(name, status):
    val_dict = get_device_params(name)
    if name == "dimmer":
        if status == True:
            return val_dict["on"]
        elif status == False:
            return val_dict["off"]
        else:
            return val_dict["level"]
    else:
        if status == True:
            return val_dict["on"]
        elif status == False:
            return val_dict["off"]
        else:
            return val_dict["battery"]

def value_on_door(name, status):
    val_dict = get_device_params(name)
    if status == True:
        return val_dict["on"]
    elif status == False:
        return val_dict["off"]
    elif status == "True":
        return val_dict["sensor"]
    else:
        return val_dict["level"]

def value_on_light(name, status):
    val_dict = get_device_params(name)
    if status == True:
        return val_dict["on"]
    elif status == False:
        return val_dict["off"]
    elif status == "set":
        return val_dict["set"]
    else:
        return val_dict["level"]

def value_on_multi(name, status):  
    val_dict = get_device_params(name)      
    if status == "True":
        return val_dict["sensor"]
    elif status == True:
        return val_dict["on"]
    elif status == False:
        return val_dict["off"]
    else:
        return val_dict["battery"]

def get_device_values(name, status):
    if name == "switch":
        return value_on_switch(name, status)
    if name == "dimmer" or name == "alarm" or name == "flood":
        return value_on_dimmer_alarm_flood(name, status)
    if name == "door":
        return value_on_door(name, status)
    if name == "light":
        return value_on_light(name, status)
    if name == "multi":
        return value_on_multi(name, status)

""" pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_bin_switch/ad:143_0 
{"ctime":"2018-05-09T15:42:49+0200",
 "props":{},
 "serv":"out_bin_switch",
 "tags":[],
 "type":"evt.binary.report",
 "val":true,"val_t":
 "bool"
} """

def dump_device_On_report(device, address, status):
    value = get_device_values(device, status)
    key = list(value)
    topic = "pt:j1/mt:evt/rt:dev/rn:{}/ad:1/sv:{}/ad:{}_0".format("emul", value[key[0]], address)

    return \
      topic, {
        "ctime": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "props": {},
        "serv": value[key[0]],
        "tags": [],
        "type": key[0],
        "val": status,
        "val_t": "bool"
    }
    
def print_mqtt(topic, payload):
    print("Topic:", topic)
    formatted = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
    
    try:
        from pygments import highlight, lexers, formatters
        print(highlight(formatted, lexers.JsonLexer(), formatters.TerminalFormatter()))
    except:
        print(formatted)
        
def generate_inclusion_report(name, address, req):
    Log("generate_inclusion_report : name : " + name)
    Log("generate_inclusion_report : address : " + address)
    
    directory = "static/prop_files/selected_device_files"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as exc: # Python >2.5
        Log("generate_inclusion_report : devices_file : Error!")
    
    Log("generate_inclusion_report : directory : " + directory)

    devices_file = "static/prop_files/selected_device_files/" + address + "_incl.json"
    Log("generate_inclusion_report : devices_file : " + devices_file)
    topic = "pt:j1/mt:evt/rt:ad/rn:{}/ad:{}".format("emul", address)
    report = dump_inclusion_report(get_services(name), name, req, address)
    
    Log("generate_inclusion_report : devices_file : " + devices_file)
    Log("generate_inclusion_report : topic : " + topic)
    Log("generate_inclusion_report : report : " + str(report))
    
    """ with open(devices_file, "w+") as jsonfile:
        json.dump(report, jsonfile)
    jsonfile.close() """
    
    Log("generate_inclusion_report : Done!")
    
    return topic, report
    
def generate_exclusion_report(address):
    Log("generate_exclusion_report : address : " + address)
    
    devices_file = "static/prop_files/selected_device_files/" + address + "_excl.json"
    topic = "pt:j1/mt:evt/rt:ad/rn:{}/ad:1".format("emul")            
    report = dump_exclusion_report(address)
    
    Log("generate_exclusion_report : devices_file : " + devices_file)
    Log("generate_exclusion_report : topic : " + topic)
    Log("generate_exclusion_report : report : " + str(report))
    
    """ with open(devices_file, "w+") as jsonfile:
        json.dump(report, jsonfile)
    jsonfile.close() """
    
    Log("generate_exclusion_report : Done!")
    
    return topic, report
 
def generate_trigger_report(event, address, device, status):
    Log("generate_trigger_report : address : " + address)
    Log("generate_trigger_report : event : " + event)
    Log("generate_trigger_report : device : " + device)
    Log("generate_trigger_report : status : " + str(status))
    
    devices_file = "static/prop_files/selected_device_files/" + address + "_trig.json"
    
    triggers = []
    if os.path.exists(devices_file):
        triggers = json.load(open(devices_file))
        Log("generate_trigger_report : triggers : " + str(triggers))
    
    topic, report = dump_trigger_report(device, address, event, status, event)
    
    Log("generate_trigger_report : devices_file : " + devices_file)
    Log("generate_trigger_report : topic : " + topic)
    Log("generate_trigger_report : report : " + str(report))
    
    triggers.append(report)
    Log("generate_trigger_report : triggers : " + str(triggers))
    """ with open(devices_file, 'w+') as jsonfile:
        json.dump(triggers, jsonfile)
    jsonfile.close() """
    
    Log("generate_trigger_report : Done!")
    
    return topic, report   

def generate_device_On_report(device, address, status):
    Log("generate_device_on_report : address : " + address)
    Log("generate_device_on_report : device : " + device)
    Log("generate_device_on_report : status : " + str(status))

    topic, report = dump_device_On_report(device, address, status)
    Log("generate_device_on_report : topic : " + topic)
    Log("generate_device_on_report : report : " + str(report))
    Log("generate_device_on_report : Done!")

    return topic, report