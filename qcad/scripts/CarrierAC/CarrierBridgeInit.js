function init(basePath) {
    var action = new RGuiAction(
        qsTranslate("CarrierBridge", "&Carrier AC Bridge"),
        RMainWindowQt.getMainWindow()
    );
    action.setRequiresDocument(true);
    action.setScriptFile(basePath + "/CarrierBridge.js");
    action.setStatusTip(qsTranslate("CarrierBridge", "Inspect the open drawing with Carrier AC Selector"));
    action.setDefaultCommands(["carrierbridge", "hvacbridge"]);
    action.setGroupSortOrder(3800);
    action.setSortOrder(300);
    action.setWidgetNames([
        "MiscDevelopmentMenu",
        "MiscDevelopmentToolBar",
        "MiscDevelopmentToolsPanel"
    ]);
}
