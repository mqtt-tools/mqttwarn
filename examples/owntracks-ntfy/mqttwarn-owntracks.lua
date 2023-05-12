--[[
Forward OwnTracks low-battery warnings to ntfy.
https://mqttwarn.readthedocs.io/en/latest/examples/owntracks-battery/readme.html
--]]

-- mqttwarn filter function, returning true if the message should be ignored.
-- In this case, ignore all battery level telemetry values above a certain threshold.
function owntracks_batteryfilter(topic, message)
    local ignore = true

    -- Decode inbound message.
    local data = json.decode(message)

    -- Evaluate filtering rule.
    if data ~= nil and data.batt ~= nil then
        ignore = tonumber(data.batt) > 20
    end

    return ignore
end

-- Status message.
print("Loaded Lua module.")

-- Export symbols.
return {
    owntracks_batteryfilter = owntracks_batteryfilter,
}
