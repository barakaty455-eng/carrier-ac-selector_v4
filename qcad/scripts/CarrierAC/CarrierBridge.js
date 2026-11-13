/* Carrier AC Selector bridge action for QCAD.
 *
 * Configure CARRIER_HAP_REPORT in QCAD's environment, then run this action
 * while a DXF document is open. The Python bridge performs the authoritative
 * CAD/HAP inspection; QCAD remains responsible for the drawing document.
 */
function CarrierBridge(guiAction) {
    this.guiAction = guiAction;
}

CarrierBridge.prototype.beginEvent = function() {
    var di = this.guiAction.getDocumentInterface();
    if (isNull(di) || isNull(di.getDocument())) {
        EAction.handleUserWarning("Open a DXF drawing before running Carrier Bridge.");
        this.terminate();
        return;
    }

    var cadPath = di.getDocument().getFileName();
    var hapPath = QProcessEnvironment.systemEnvironment().value("CARRIER_HAP_REPORT", "");
    var client = QProcessEnvironment.systemEnvironment().value(
        "CARRIER_BRIDGE_CLIENT", "tools/cad_bridge.py"
    );
    if (cadPath === "" || hapPath === "") {
        EAction.handleUserWarning(
            "Set CARRIER_HAP_REPORT and save the drawing before running Carrier Bridge."
        );
        this.terminate();
        return;
    }

    var process = new QProcess();
    var args = [client, "inspect", "--cad", cadPath, "--hap", hapPath];
    process.start("python3", args);
    process.waitForFinished(120000);
    var output = process.readAllStandardOutput();
    var error = process.readAllStandardError();
    if (process.exitCode() !== 0) {
        EAction.handleUserWarning("Carrier bridge failed: " + error);
    }
    else {
        EAction.handleUserMessage(output);
    }
    this.terminate();
};

CarrierBridge.init = function(basePath) {
    var action = new RGuiAction(qsTr("&Carrier AC Bridge"), RMainWindowQt.getMainWindow());
    action.setRequiresDocument(true);
    action.setScriptFile(basePath + "/CarrierBridge.js");
    action.setGroupSortOrder(70000);
    action.setSortOrder(100);
    action.setWidgetNames(["CarrierACMenu"]);
};
