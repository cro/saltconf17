-- Basic Lua script for the NodeMCU to scan for Wi-Fi Access Points.

-- This global holds the current table of Access Points.  It gets updated
-- via callback whenever wifi.sta.getap completes its scan 
APTABLE = {}

-- Callback target for wifi.sta.getap.
-- This function gets called with the results of the AP scan
-- then we save it into the global to make it available to ap_as_json()
function cacheap(t)
  APTABLE = t
end

-- This function is called every 15 seconds to start the AP scan process
function getap()
  cfg = {}

  -- Include APs that are not broadcasting an SSID
  cfg["show_hidden"] = 1
  wifi.sta.getap(cfg, 1, cacheap)
end

-- Entrypoint to create the timer-based callback
-- to scan for APs
function startup()
  tmr.register(1, 30000, tmr.ALARM_AUTO, getap)
  tmr.start(1)
end

-- Code below is the equivalent of a main()

-- Ensure the Wi-Fi hardware is in the right mode
wifi.setmode(wifi.STATION, true)
wifi.setphymode(wifi.PHYMODE_G)

print("NodeMCU ready to scan for Wi-Fi Access Points in 5 seconds")

-- Make sure that the getap timer is not somehow still configured/running.
tmr.unregister(1)

-- Wait 5 seconds in case the user needs to abort, then call startup()
maintimer = tmr.create():alarm(5000, tmr.ALARM_SINGLE, startup)



