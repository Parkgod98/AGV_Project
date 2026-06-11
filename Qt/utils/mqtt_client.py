# mqtt_client.py
import json
import traceback
import paho.mqtt.client as mqtt
from PySide6.QtCore import QObject, Signal


class MqttClient(QObject):
    connected = Signal()
    disconnected = Signal()
    messageReceived = Signal(str, str)  # topic, payload
    log = Signal(str)                  # 로그용(선택)
    error = Signal(str)                # 예외/에러용(선택)

    def __init__(self, host="localhost", port=1883, client_id="hmi"):
        super().__init__()
        self.host = host
        self.port = port

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self._loop_started = False

    def connect_to_host(self):
        """
        ⚠️ 기존처럼 client.connect()를 쓰면 동기 블로킹이 발생할 수 있음.
        -> connect_async + loop_start로 UI-blocking 방지
        """
        try:
            self.log.emit(f"[MQTT] connect_async {self.host}:{self.port}")
            # non-blocking connect
            self.client.connect_async(self.host, self.port, keepalive=30)

            # network loop thread start
            if not self._loop_started:
                self.client.loop_start()
                self._loop_started = True

        except Exception as e:
            self.error.emit("[MQTT] connect_to_host failed: " + repr(e))
            self.error.emit(traceback.format_exc())
            # 연결 실패는 disconnected 상태로 취급
            self.disconnected.emit()

    def disconnect_from_host(self):
        try:
            if self._loop_started:
                self.client.loop_stop()
                self._loop_started = False
            self.client.disconnect()
        except Exception as e:
            self.error.emit("[MQTT] disconnect_from_host failed: " + repr(e))
            self.error.emit(traceback.format_exc())

    def subscribe(self, topic, qos=0):
        try:
            self.client.subscribe(topic, qos)
            self.log.emit(f"[MQTT] SUB {topic} (qos={qos})")
        except Exception as e:
            self.error.emit(f"[MQTT] subscribe failed: {topic} ({e})")

    def publish(self, topic, payload, qos=0, retain=False):
        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload, ensure_ascii=False)
            elif not isinstance(payload, str):
                payload = str(payload)
            self.client.publish(topic, payload, qos=qos, retain=retain)
        except Exception as e:
            self.error.emit(f"[MQTT] publish failed: {topic} ({e})")
            self.error.emit(traceback.format_exc())

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.log.emit("[MQTT] Connected (rc=0)")
            self.connected.emit()
        else:
            self.log.emit(f"[MQTT] Connect failed (rc={rc})")
            self.disconnected.emit()

    def _on_disconnect(self, client, userdata, rc):
        self.log.emit(f"[MQTT] Disconnected (rc={rc})")
        self.disconnected.emit()

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore")
        self.messageReceived.emit(msg.topic, payload)
