from __future__ import absolute_import
import octoprint.plugin
import octoprint.printer
import octoprint.printer.profile
import threading, time, datetime


# region Класс для сравнения времени
class Date:
	"""
	Класс даты
	"""

	def __init__(self, hour: int, minute: int) -> None:
		"""
		Инициализация класса даты
		\n
		:param hour: [int] => час
		:param minute: [int] => минута
		"""
		self.hour = hour
		self.minute = minute

	def __str__(self):
		return f"{self.hour}:{self.minute}"

	def __eq__(self, other):
		return (self.hour == other.hour and self.minute == other.minute)

	def __ge__(self, other):
		return self.__eq__(other) or self.__gt__(other)

	def __gt__(self, other):
		s_hour = self.hour
		if (self.hour == 0): s_hour = 24

		o_hour = other.hour
		if (other.hour == 0): o_hour = 24

		if (s_hour > o_hour):
			return True
		elif (s_hour == o_hour):
			return (self.minute > other.minute)

		return False
#endregion

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
		self.last_TimeState: int = -1
		self.currentSettings: dict = self._settings.settings.get(["plugins", "brightcontrol"], merged=True)
		self.Update()

	def IsCurrentTime(self, timeOn: str, timeOff: str) -> int:
		timeCurrent_T = datetime.datetime.now()
		timeCurrent_T: Date = Date(timeCurrent_T.hour, timeCurrent_T.minute)

		timeOn_T = datetime.datetime.strptime(timeOn, "%H:%M")
		timeOn_T: Date = Date(timeOn_T.hour, timeOn_T.minute)

		timeOff_T = datetime.datetime.strptime(timeOff, "%H:%M")
		timeOff_T: Date = Date(timeOff_T.hour, timeOff_T.minute)

		if (timeOn_T <= timeCurrent_T <= timeOff_T): return self.TimeState.DAY
		else: return self.TimeState.NIGHT

	def ChangeLedBright(self, timeState: int) -> None:
		"""
		Изменить яркость подсветки
		\n
		:param timeState: [int] => стадия текущего времени
		:return: None
		"""
		if (timeState == self.TimeState.DAY):
			timeOn_Bright = int(self.currentSettings["timeOn_Bright"])
			self._logger.info(f"[DEBUG] CHANGE STATE -> {timeState} -> DAY -> {timeOn_Bright}")

			self._printer.commands(f"""M355 P{round(timeOn_Bright * 2.55)} S1""")
		else:
			timeOff_Bright = int(self.currentSettings["timeOff_Bright"])
			self._logger.info(f"[DEBUG] CHANGE STATE -> {timeState} -> NIGHT -> {timeOff_Bright}")

			if (timeOff_Bright == 0):
				self._printer.commands(f"""M355 P0 S0""")
			else:
				self._printer.commands(f"""M355 P{round(timeOff_Bright * 2.55)} S1""")

	@Thread
	def Update(self) -> None:
		"""
		Вызов циклической функции раз в 5 секунд
		\n
		:return: None
		"""

		b_isSend: bool = False

		while (True):
			try:
				time.sleep(5)

				timeState: int = self.IsCurrentTime(self.currentSettings["timeOn"], self.currentSettings["timeOff"])
				# self._logger.info(f"[DEBUG] CURRENT STATE -> {timeState} -> {currentSettings}")

				if (self.last_TimeState != timeState):
					self.ChangeLedBright(timeState)

					self.last_TimeState = timeState
			except Exception as exception:
				print(exception)
				return

	def get_settings_defaults(self):
		return {
			"timeOn": "06:30",
			"timeOff": "20:40",
			"timeOff_Bright": "10",
			"timeOn_Bright": "100",
		}

	def get_template_configs(self):
		return [
			# dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def on_settings_save(self, data):
		self._logger.info(data)

		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		self.currentSettings: dict = self._settings.settings.get(["plugins", "brightcontrol"], merged=True)
		self.ChangeLedBright(self.last_TimeState)

	def get_assets(self):
		return dict(
			js=["js/brightcontrol.js"],
			css=["css/brightcontrol.css"],
			less=["less/brightcontrol.less"]
		)

__plugin_name__ = "Bright Control"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = BrightControlPlugin()
