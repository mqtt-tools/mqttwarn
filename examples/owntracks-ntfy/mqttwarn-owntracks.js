/**
 *
 * Forward OwnTracks low-battery warnings to ntfy.
 * https://mqttwarn.readthedocs.io/en/latest/examples/owntracks-battery/readme.html
 *
 */

// mqttwarn filter function, returning true if the message should be ignored.
// In this case, ignore all battery level telemetry values above a certain threshold.
function owntracks_batteryfilter(topic, message) {
    let ignore = true;
    let data;

    // Decode inbound message.
    try {
        data = JSON.parse(message);
    } catch {
        data = null;
    }

    // Evaluate filtering rule.
    if (data && "batt" in data && data.batt !== null) {
        ignore = Number.parseFloat(data.batt) > 20;
    }

    return ignore;
}

// Status message.
console.log("Loaded JavaScript module.");

// Export symbols.
module.exports = {
    "owntracks_batteryfilter": owntracks_batteryfilter,
};
