from __future__ import absolute_import
import octoprint.plugin
import octoprint.printer
import octoprint.printer.profile
import threading, time

def Thread(func):
    """
    Декоратор Thread, для запуска функции в отдельном потоке
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper

class BrightControlPlugin(octoprint.plugin.StartupPlugin, octoprint.plugin.TemplatePlugin, octoprint.plugin.SettingsPlugin, octoprint.plugin.AssetPlugin):
	class TimeState:
		NIGHT: int = 0
		"""
		Ночь
		"""
		DAY: int = 1
		"""
		День
		"""

	def on_after_startup(self):
		self.Update()

	def IsCurrentTime(self, timeOn: str, timeOff: str) -> int:
		timeCurrent_T = time.gmtime()
		timeOn_T = time.strptime(timeOn, "%H:%M")
		timeOff_T = time.strptime(timeOn, "%H:%M")

		if (timeOn_T < timeOff_T):
			if (timeOn_T < timeCurrent_T < timeOff_T): return self.TimeState.DAY
			else: return self.TimeState.NIGHT
		else:
			if (timeOff_T < timeCurrent_T < timeOn_T): return self.TimeState.NIGHT
			else: return self.TimeState.DAY

	@Thread
	def Update(self) -> None:
		"""
		Вызов циклической функции раз в 5 секунд
		\n
		:return: None
		"""

		b_isSend: bool = False
		last_TimeState: int = -1

		while (True):
			try:
				time.sleep(5)
				currentSettings: dict = self._settings.settings.get(["plugins", "brightcontrol"])
				timeState: int = self.IsCurrentTime(currentSettings["timeOn"], currentSettings["timeOff"])

				if (last_TimeState != timeState):
					if (timeState == self.TimeState.DAY):
						self._printer.commands(f"""M355 P{int(currentSettings["timeOn_Bright"]) * 2.55} S1""")
					else:
						timeOff_Bright = int(currentSettings["timeOff_Bright"])
						if (timeOff_Bright == 0):
							self._printer.commands(f"""M355 P0 S0""")
						else:
							self._printer.commands(f"""M355 P{timeOff_Bright * 2.55} S1""")

					last_TimeState = timeState
			except Exception as exception:
				print(exception)
				return

	def get_settings_defaults(self):
		return {
			"timeOn": "6:30",
			"timeOff": "20:40",
			"timeOff_Bright": 10,
			"timeOn_Bright": 100,
		}

	def get_template_configs(self):
		return [
			# dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def on_settings_save(self, data):
		self._logger.info(data)
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

	def get_assets(self):
		return dict(
			js=["js/brightcontrol.js"],
			css=["css/brightcontrol.css"],
			less=["less/brightcontrol.less"]
		)

__plugin_name__ = "Bright Control"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = BrightControlPlugin()
