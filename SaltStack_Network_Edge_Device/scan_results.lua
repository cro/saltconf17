
-- This is the file that will get called when Salt wants an updated
-- list of access points.  The seemingly superfluous print statements are
-- there to help parse the results
print("=+-=+-=+-=+-=+-=+-=+=+-=+-=+-=+-=+-=+-=+--=+-=+-=+-=+-=+-=+-=+-")
if next(APTABLE) ~= nil then
    local ssid, rssi, authmode, channel
    for bssid,v in pairs(APTABLE) do
        ssid, rssi, authmode, channel = string.match(v, "([^,]+),([^,]+),([^,]+),([^,]+)")
	if rssi == nil then
	    ssid = "Hidden"
	    rssi, authmode, channel = string.match(v, ",([^,]+),([^,]+),([^,]+)")
	end
	print("{\"ssid\":\""..ssid.."\",\"bssid\":\""..bssid.."\",\"rssi\":\""..rssi.."\",\"authmode\":\""..authmode.."\",\"channel\":\""..channel.."\"}")
    end
else
    print("None")
end
print("--done--")
