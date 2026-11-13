/* Carrier AC Selector bridge action for QCAD.
 *
 * Configure CARRIER_HAP_REPORT in QCAD's environment, then run this action
 * while a DXF document is open. The Python bridge performs the authoritative
 * CAD/HAP inspection; QCAD remains responsible for the drawing document.
 */
include("scripts/EAction.js");

function CarrierBridge(guiAction) {
    EAction.call(this, guiAction);
}

CarrierBridge.prototype = new EAction();
CarrierBridge.includeBasePath = includeBasePath;

CarrierBridge.prototype.beginEvent = function() {
    EAction.prototype.beginEvent.call(this);
    var di = this.guiAction.getDocumentInterface();
    if (isNull(di) || isNull(di.getDocument())) {
        EAction.handleUserWarning("Open a DXF drawing before running Carrier Bridge.");
        this.terminate();
        return;
    }

    var cadPath = di.getDocument().getFileName();
    var hapPath = QProcessEnvironment.systemEnvironment().value("CARRIER_HAP_REPORT", "");
    var python = QProcessEnvironment.systemEnvironment().value("CARRIER_BRIDGE_PYTHON", "python3");
    var client = QProcessEnvironment.systemEnvironment().value("CARRIER_BRIDGE_CLIENT", "");
    if (cadPath === "" || hapPath === "") {
        EAction.handleUserWarning(
            "Set CARRIER_HAP_REPORT and save the drawing before running Carrier Bridge."
        );
        this.terminate();
        return;
    }
    if (client === "") {
        EAction.handleUserWarning(
            "Set CARRIER_BRIDGE_CLIENT to the absolute path of tools/cad_bridge.py."
        );
        this.terminate();
        return;
    }

    var process = new QProcess();
    var args = [client, "inspect", "--cad", cadPath, "--hap", hapPath];
    process.start(python, args);
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
