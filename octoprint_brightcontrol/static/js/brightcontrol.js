$(function() {
    function BrightControlViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.timeOn = ko.observable();
        self.timeOn_Bright = ko.observable();

        self.timeOff = ko.observable();
        self.timeOff_Bright = ko.observable();

        self.timeZone = ko.observable();

        self.onBeforeBinding = function() {
            self.timeOn(self.settings.settings.plugins.brightcontrol.timeOn());
            self.timeOff(self.settings.settings.plugins.brightcontrol.timeOff());

            self.timeOff_Bright(self.settings.settings.plugins.brightcontrol.timeOff_Bright());
            self.timeOn_Bright(self.settings.settings.plugins.brightcontrol.timeOff_Bright());

            self.timeZone(self.settings.settings.plugins.brightcontrol.timeZone());
        }

		self.saveData = function() {
            data = {
                plugins : {
                    brightcontrol: {
                        timeOn: self.timeOn(),
                        timeOff: self.timeOff(),

                        timeOff_Bright: self.timeOff_Bright(),
                        timeOn_Bright: self.timeOn_Bright(),

                        timeZone: self.timeOn_Bright(),
                    }
                }
            };

			self.settings.saveData(data);
		}
    }

    // This is how our plugin registers itself with the application, by adding some configuration information to
    // the global variable ADDITIONAL_VIEWMODELS
    ADDITIONAL_VIEWMODELS.push([
        // This is the constructor to call for instantiating the plugin
        BrightControlViewModel,

        // This is a list of dependencies to inject into the plugin, the order which you request here is the order
        // in which the dependencies will be injected into your view model upon instantiation via the parameters
        // argument
        ["settingsViewModel"],

        // Finally, this is the list of all elements we want this view model to be bound to.
        [document.getElementById("settings_plugin_settings")]
    ]);
});
