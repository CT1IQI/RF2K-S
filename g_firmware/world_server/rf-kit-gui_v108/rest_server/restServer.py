import json
from threading import Thread

import interface
from bottle.bottle import run, ServerAdapter, get, route, response, request
from config import Config
from data import Data, BAND_VALUES
from main_screen.tuners import Tuner
from operationalInterface import OperationalInterfaceControl, OperationalInterface

from sleepTimer import SleepTimer


class RestServerSupport:
    def __init__(self, operate_standby_function, reset_function, antenna_change_allowed_check, set_internal_antenna_function):
        self.operateStandbyFunction = operate_standby_function
        self.resetFunction = reset_function
        self.antennaSetAllowedCheck = antenna_change_allowed_check
        self.setInternalAntennaFunction = set_internal_antenna_function
        self.restServer = None

    def start_rest_server(self):
        if self.restServer is None:
            self.restServer = RestServer(self.operateStandbyFunction, self.resetFunction, self.antennaSetAllowedCheck, self.setInternalAntennaFunction)
            self.restServer.start()

    def stop_rest_server(self):
        if self.restServer is not None:
            self.restServer.stop()
            self.restServer = None


def disabled_conflict():
    return error(409, {
        "status": "409 Conflict",
        "reason": "currently disabled"
    })


def error(status, response_dict):
    response.status = status
    response.content_type = 'application/json'
    return json.dumps(response_dict)


def handle_sleep():
    SleepTimer.get_instance().reset()
    if SleepTimer.get_instance().activeSleepScreen is not None:
        SleepTimer.get_instance().activeSleepScreen.wakeup()


def value_unit(value, unit, decimal_places_count=None):
    return {
        "value": value if decimal_places_count is None else with_decimal_places(value, decimal_places_count),
        "unit": unit
    }


def value_max_unit(value, max_value, unit, decimal_places_count=None):
    return {
        "value": value if decimal_places_count is None else with_decimal_places(value, decimal_places_count),
        "max_value": max_value if decimal_places_count is None else with_decimal_places(max_value, decimal_places_count),
        "unit": unit
    }


def with_decimal_places(number, decimal_places_count):
    if decimal_places_count == 0:
        return int(number)
    factor = pow(10, decimal_places_count)
    return (int(number * factor)) * 1.0 / factor


def get_info():
    return {
        "device": str(Data.getInstance().generation),
        "software_version": {
            "GUI": Data.getInstance().guiVersion,
            "controller": Data.getInstance().version
        },
        "custom_device_name": Config.get_instance().savedCustomDeviceName
    }


def get_data():
    values = {
        "band": value_unit(BAND_VALUES[Data.getInstance().curBand], "m"),
        "frequency": value_unit(Data.getInstance().f_m // 1000, "kHz"),
        "status": str(Data.getInstance().errorState)
        # ptt
        #bias
    }
    return values


def get_antenna():
    if Data.getInstance().useExternalAntenna:
        antenna = {
            "type": "EXTERNAL",
            "number": Data.getInstance().curAntenna + 1
        }
    else:
        antenna = {
            "type": "INTERNAL",
            "number": Data.getInstance().curAntenna + 1
        }
    return antenna


all_antennas = [
    {
        "type": "INTERNAL",
        "number": i + 1
    }
    for i in range(4)
]
all_antennas.append({"type": "EXTERNAL"})



def get_antennas_with_state():
    ext_active = Data.getInstance().useExternalAntenna
    active_number = Data.getInstance().curAntenna + 1
    antennas = [
        {
            "type": "INTERNAL",
            "number": i + 1,
            "state": "ACTIVE" if (i + 1 == active_number and not ext_active)
            else "AVAILABLE" if antenna_is_selected
            else "DISABLED"
        }
        for i, antenna_is_selected
        in enumerate(Config.get_instance().savedSelectedAntennasPerBand[Data.getInstance().curBand])
    ]
    external_antenna = {
        "type": "EXTERNAL"
    }
    if ext_active:
        external_antenna["number"] = active_number
        external_antenna["state"] = "ACTIVE"
    else:
        external_antenna["state"] = "AVAILABLE"

    antennas.append(external_antenna)
    return {"antennas": antennas}


def get_operational_interface():
    error_message = OperationalInterfaceControl.operationalInterface.errorString
    op_int = {
        "operational_interface": OperationalInterfaceControl.operationalInterface.currentOperationalInterface.name[:4]
    }
    if error_message:
        op_int["error"] = error_message
    return op_int


def set_operational_interface():
    handle_sleep()
    request_json = request.json
    operational_interface = request_json.get("operational_interface") if request_json is not None else None
    available_interfaces = dict([(oi.name[:4], oi) for oi in OperationalInterface])
    new_interface = available_interfaces.get(operational_interface)
    if new_interface is None:
        return error(400, {
            "status": "400 Bad Request",
            "reason": "JSON request body with key 'operational_interface' and value one of "+"/".join(["'" + key + "'" for key in available_interfaces.keys()])+" required"
        })
    OperationalInterfaceControl.operationalInterface.switch_operational_interface(new_interface)
    return get_operational_interface()


def get_power():
    return {
        "temperature": value_unit(Data.getInstance().temperature, "°C", 1),
        "voltage": value_unit(Data.getInstance().voltage, "V", 1),
        "current": value_unit(Data.getInstance().get_truncated_current(), "A", 1),
        "forward": value_max_unit(Data.getInstance().P_F, Data.getInstance().overall_max_P_F, "W", 0),
        "reflected": value_max_unit(Data.getInstance().P_R, Data.getInstance().overall_max_P_R, "W", 0),
        "swr": value_max_unit(Data.getInstance().SWR, Data.getInstance().overall_max_SWR, "", 2)
    }


def get_tuner():
    tuner_state = Data.getInstance().tunerState
    sub_type = Tuner.TunerSubType(Data.getInstance().K)
    if Data.getInstance().errorState == Data.ErrorState.NOT_TUNED:
        tuner = {
            "mode": tuner_state.name,
            "setup": "NOT TUNED"
        }
    elif tuner_state == Data.TunerState.OFF or tuner_state == Data.TunerState.BYPASS:
        tuner = {
            "mode": tuner_state.name
        }
    elif Data.getInstance().bypass or sub_type == Tuner.TunerSubType.BYPASS:
        tuner = {
            "mode": tuner_state.name,
            "setup": Tuner.TunerSubType.BYPASS.name,
            "tuned_frequency": value_unit(Data.getInstance().f_t // 1000, "kHz"),
            "segment_size": value_unit(Data.getInstance().segmentSize, "kHz")
        }
    else:
        tuner = {
            "mode": tuner_state.name,
            "setup": sub_type.name,
            "L": value_unit(Data.getInstance().L, "nH"),
            "C": value_unit(Data.getInstance().C, "pF"),
            "tuned_frequency": value_unit(Data.getInstance().f_t // 1000, "kHz"),
            "segment_size": value_unit(Data.getInstance().segmentSize, "kHz")
        }
    return tuner


def get_operate_standby():
    operate_mode = "OPERATE" if Data.getInstance().inOperate else "STANDBY"
    return {
        "operate_mode": operate_mode
    }


class RestServer(Thread):
    def __init__(self, operate_standby_function, reset_function, antenna_change_allowed_check, set_internal_antenna_function):
        super().__init__(target=self.serve)
        super().setDaemon(True)
        self.underlyingServer = None
        self.operateStandbyFunction = operate_standby_function
        self.resetFunction = reset_function
        self.antennaSetAllowedCheck = antenna_change_allowed_check
        self.setInternalAntennaFunction = set_internal_antenna_function

        route('/info', ['GET'], get_info)
        route('/data', ['GET'], get_data)
        route('/power', ['GET'], get_power)
        route('/tuner', ['GET'], get_tuner)
        route('/antennas', ['GET'], get_antennas_with_state)
        route('/antennas/active', ['GET'], get_antenna)
        route('/antennas/active', ['PUT'], self.set_antenna)
        route('/operational-interface', ['GET'], get_operational_interface)
        route('/operational-interface', ['PUT'], set_operational_interface)
        route('/error/reset', ['POST'], self.reset_error)
        route('/operate-mode', ['GET'], get_operate_standby)
        route('/operate-mode', ['PUT'], self.set_operate_standby)

    def serve(self):
        self.underlyingServer = StoppableWSGIRefServer()
        run(server=self.underlyingServer, quiet=True)

    def stop(self):
        self.underlyingServer.stop()

    def reset_error(self):
        handle_sleep()
        success = self.resetFunction()
        if not success:
            return disabled_conflict()

    def set_operate_standby(self):
        handle_sleep()
        request_json = request.json
        operate_mode = request_json.get("operate_mode") if request_json is not None else None
        if operate_mode == "OPERATE":
            to_operate = True
        elif operate_mode == "STANDBY":
            to_operate = False
        else:
            return error(400, {
                "status": "400 Bad Request",
                "reason": "JSON request body with key 'operate_mode' and value one of 'OPERATE'/'STANDBY' required"
            })
        success = self.operateStandbyFunction(to_operate)
        if not success:
            return disabled_conflict()
        Data.getInstance().fetch_data_once()
        return get_operate_standby()

    def set_antenna(self):
        handle_sleep()
        request_json = request.json
        if request_json in [
            {
                "type": ant.get("type"),
                "number": ant.get("number")
            } if ant.get("type") == "INTERNAL"
            else {
                "type": ant.get("type")
            }
            for ant in get_antennas_with_state().get("antennas")
            if ant.get("state") == "AVAILABLE" or ant.get("state") == "ACTIVE"
        ]:
            if not self.antennaSetAllowedCheck():
                return disabled_conflict()
            new_type = request_json.get("type")
            if new_type == "EXTERNAL":
                interface.set_use_ext_antenna(1)
            else:
                interface.set_use_ext_antenna(0)
                new_antenna_index = request_json.get("number") - 1
                success = self.setInternalAntennaFunction(new_antenna_index)
                if not success:
                    return disabled_conflict()
            Data.getInstance().fetch_data_once()
            return get_antenna()
        elif request_json in all_antennas:
            return error(409, {
                "status": "409 Conflict",
                "reason": "The requested antenna is not available at the moment."
            })
        else:
            return error(400, {
                "status": "400 Bad Request",
                "reason": 'Not a valid antenna to set.'
            })


class StoppableWSGIRefServer(ServerAdapter):
    def __init__(self, host='0.0.0.0', port=8080, **options):
        super().__init__(host=host, port=port, options=options)
        self.srv = None

    def run(self, app): # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self): # Prevent reverse DNS lookups please.
                return self.client_address[0]
            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)

        if ':' in self.host: # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        self.srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv.serve_forever()

    def stop(self):
        if self.srv is not None:
            self.srv.shutdown()
            self.srv = None


