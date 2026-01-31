/**
 * AC Dashboard Universal JavaScript Client
 * Handles all telemetry fields for any dashboard theme.
 *
 * Usage:
 *   <script src="dashboard.js"></script>
 *
 * That's it! Just use the element IDs listed below and everything works automatically.
 *
 * Supported Element IDs:
 *   - rpm, rpmFill, gear, speed
 *   - abs, tc, drs, pitLimiter
 *   - fuelFill, fuelRem, fuelPerLap, fuelCap
 *   - waterTemp, lap, brakeBias, tyreType
 *   - laptime, timeDiff, bestLap
 *   - tyreFLPressure, tyreFRPressure, tyreRLPressure, tyreRRPressure
 *   - tyreFLTemp, tyreFRTemp, tyreRLTemp, tyreRRTemp
 *   - status (connection indicator)
 */

(function() {
    'use strict';

    let ws = null;
    let dataHandler = null;
    let connectionHandler = null;

    /**
     * Register a callback for when telemetry data is received (optional)
     */
    function onDataUpdate(callback) {
        dataHandler = callback;
    }

    /**
     * Register a callback for connection state changes (optional)
     */
    function onConnectionChange(callback) {
        connectionHandler = callback;
    }

    /**
     * Get DOM element by ID
     */
    function getElement(id) {
        return document.getElementById(id);
    }

    /**
     * Update RPM display
     */
    function updateRPM(data) {
        const rpmEl = getElement('rpm');
        const rpmFillEl = getElement('rpmFill');

        if (rpmEl) rpmEl.textContent = data.rpm || 0;
        if (rpmFillEl) rpmFillEl.style.width = (data.rpmPercent || 0) + '%';
    }

    /**
     * Update gear display
     */
    function updateGear(data) {
        const gearEl = getElement('gear');
        if (!gearEl) return;

        const gear = data.gear;
        let gearText = 'N';
        let gearClass = 'N';

        if (gear === 0) {
            gearText = 'R';
            gearClass = 'R';
        } else if (gear === 1) {
            gearText = 'N';
            gearClass = 'N';
        } else if (gear >= 2 && gear <= 8) {
            gearText = (gear - 1).toString();
            gearClass = (gear - 1).toString();
        }

        gearEl.textContent = gearText;
        gearEl.className = gearEl.className.replace(/gear-\w+/g, '').trim();
        if (gearClass) {
            gearEl.classList.add('gear-' + gearClass);
        }
    }

    /**
     * Update speed display
     */
    function updateSpeed(data) {
        const speedEl = getElement('speed');
        if (speedEl) {
            speedEl.textContent = Math.round(data.speed || 0);
        }
    }

    /**
     * Update ABS indicator
     */
    function updateABS(data) {
        const absEl = getElement('abs');
        const absValueEl = getElement('absValue');
        const absTextEl = getElement('absText');
        const iconLowEl = getElement('icon-low');

        if (absEl) {
            absEl.classList.toggle('active', data.abs > 0.1);
        }
        if (absValueEl) {
            absValueEl.textContent = (data.abs !== undefined && data.abs !== null) ? String(data.abs) : String(data.abs_physics || 0);
        }
        if (absTextEl) {
            absTextEl.textContent = data.abs > 0.1 ? 'ON' : 'OFF';
        }
        if (iconLowEl) {
            iconLowEl.classList.toggle('hidden', data.abs <= 0.1);
        }
    }

    /**
     * Update TC indicator
     */
    function updateTC(data) {
        const tcEl = getElement('tc');
        const tcValueEl = getElement('tcValue');
        const tcTextEl = getElement('tcText');

        if (tcEl) {
            tcEl.classList.toggle('active', data.tc > 0.1);
        }
        if (tcValueEl) {
            tcValueEl.textContent = (data.tc !== undefined && data.tc !== null) ? String(data.tc) : String(data.tc_physics || 0);
        }
        if (tcTextEl) {
            tcTextEl.textContent = data.tc > 0.1 ? 'ON' : 'OFF';
        }
    }

    /**
     * Update DRS indicator
     */
    function updateDRS(data) {
        const drsEl = getElement('drs');
        const drsValueEl = getElement('drsValue');
        const drsTextEl = getElement('drsText');
        const dimValueEl = getElement('dimValue');
        const iconHighEl = getElement('icon-high');

        const active = data.drs > 0.5;

        if (drsEl) {
            drsEl.classList.toggle('active', active);
        }
        if (drsValueEl) {
            drsValueEl.textContent = active ? '1' : '0';
        }
        if (dimValueEl) {
            dimValueEl.textContent = active ? '1' : '0';
        }
        if (drsTextEl) {
            drsTextEl.textContent = active ? 'ON' : 'OFF';
        }
        if (iconHighEl) {
            iconHighEl.classList.toggle('hidden', !active);
        }
    }

    /**
     * Update pit limiter indicator
     */
    function updatePitLimiter(data) {
        const pitEl = getElement('pitLimiter');
        const pitValueEl = getElement('pitValue');
        const pitTextEl = getElement('pitText');
        const athValueEl = getElement('athValue');
        const iconHazardEl = getElement('icon-hazard');

        const active = data.pitLimiter > 0;

        if (pitEl) {
            pitEl.classList.toggle('danger', active);
        }
        if (pitValueEl) {
            pitValueEl.textContent = active ? '1' : '0';
        }
        if (athValueEl) {
            athValueEl.textContent = active ? '1' : '0';
        }
        if (pitTextEl) {
            pitTextEl.textContent = active ? 'ON' : 'OFF';
        }
        if (iconHazardEl) {
            iconHazardEl.classList.toggle('hidden', !active);
        }
    }

    /**
     * Update brake indicator (icon)
     */
    function updateBrake(data) {
        const iconBrakeEl = getElement('icon-brake');
        if (iconBrakeEl) {
            iconBrakeEl.classList.toggle('hidden', (data.brake || 0) <= 0.1);
        }
    }

    /**
     * Update fuel displays
     */
    function updateFuel(data) {
        const fuelFillEl = getElement('fuelFill');
        const fuelRemEl = getElement('fuelRem');
        const fuelPerLapEl = getElement('fuelPerLap');
        const fuelCapEl = getElement('fuelCap');

        if (fuelFillEl) {
            fuelFillEl.style.width = Math.round((data.fuel || 0) * 100) + '%';
        }
        if (fuelRemEl) {
            fuelRemEl.textContent = (data.fuelRem !== undefined) ? data.fuelRem.toFixed(1) : '-';
        }
        if (fuelPerLapEl) {
            fuelPerLapEl.textContent = (data.fuelPerLap > 0) ? data.fuelPerLap.toFixed(1) : '-';
        }
        if (fuelCapEl) {
            fuelCapEl.textContent = (data.fuelCap !== undefined) ? data.fuelCap.toFixed(0) : '-';
        }
    }

    /**
     * Update water temperature
     */
    function updateWaterTemp(data) {
        const waterTempEl = getElement('waterTemp');
        if (waterTempEl) {
            waterTempEl.textContent = (data.waterTemp !== undefined) ? Math.round(data.waterTemp) + '°C' : '-';
        }
    }

    /**
     * Update lap count
     */
    function updateLap(data) {
        const lapEl = getElement('lap');
        if (lapEl) {
            lapEl.textContent = String(data.lap || 0);
        }
    }

    /**
     * Update brake bias
     */
    function updateBrakeBias(data) {
        const brakeBiasEl = getElement('brakeBias');
        if (brakeBiasEl) {
            brakeBiasEl.textContent = (data.brakeBias || 0) + '%';
        }
    }

    /**
     * Update tyre type display
     */
    function updateTyreType(data) {
        const tyreTypeEl = getElement('tyreType');
        if (!tyreTypeEl) return;

        let tyreText = data.tyreCompound || data.tyreType || data.wheelType || 'DRY';
        if (typeof tyreText === 'string') {
            const upper = tyreText.toUpperCase();
            if (upper.includes('WET') || upper.includes('RAIN')) {
                tyreText = 'WET';
            } else if (upper.includes('DRY') || upper.includes('SLICK') || upper.includes('SUPER') || upper.includes('SOFT') || upper.includes('MEDIUM') || upper.includes('HARD')) {
                tyreText = 'DRY';
            }
        }
        tyreTypeEl.textContent = String(tyreText);
    }

    /**
     * Update tyre pressure
     */
    function updateTyrePressure(data) {
        if (!data.tyrePressure || data.tyrePressure.length < 4) return;

        const [fl, fr, rl, rr] = data.tyrePressure;
        const elFL = getElement('tyreFLPressure');
        const elFR = getElement('tyreFRPressure');
        const elRL = getElement('tyreRLPressure');
        const elRR = getElement('tyreRRPressure');

        if (elFL) elFL.textContent = fl.toFixed(1);
        if (elFR) elFR.textContent = fr.toFixed(1);
        if (elRL) elRL.textContent = rl.toFixed(1);
        if (elRR) elRR.textContent = rr.toFixed(1);
    }

    /**
     * Update tyre core temperature
     */
    function updateTyreTemp(data) {
        if (!data.tyreCoreTemperature || data.tyreCoreTemperature.length < 4) return;

        const [flt, frt, rlt, rrt] = data.tyreCoreTemperature;
        const tFL = getElement('tyreFLTemp');
        const tFR = getElement('tyreFRTemp');
        const tRL = getElement('tyreRLTemp');
        const tRR = getElement('tyreRRTemp');

        if (tFL) tFL.textContent = Math.round(flt);
        if (tFR) tFR.textContent = Math.round(frt);
        if (tRL) tRL.textContent = Math.round(rlt);
        if (tRR) tRR.textContent = Math.round(rrt);
    }

    /**
     * Parse ACC time format
     */
    function parseTime(timeStr) {
        if (!timeStr) return null;
        timeStr = timeStr.trim();

        // Handle "29:337" format (SS:mmm)
        if (!timeStr.startsWith(':') && timeStr.split(':').length === 2) {
            const parts = timeStr.split(':');
            const sec = parseInt(parts[0]) || 0;
            const ms = parseInt(parts[1]) || 0;
            return (sec * 1000) + ms;
        }

        // Handle ":29:337" format
        if (timeStr.startsWith(':')) {
            const parts = timeStr.split(':');
            if (parts.length === 3) {
                const sec = parseInt(parts[1]) || 0;
                const ms = parseInt(parts[2]) || 0;
                return (sec * 1000) + ms;
            }
        }

        // Handle "M:SS:mmm" format
        const parts = timeStr.split(':');
        if (parts.length === 2) {
            const min = parseInt(parts[0]) || 0;
            const secParts = parts[1].split('.');
            if (secParts.length === 2) {
                const sec = parseInt(secParts[0]) || 0;
                const ms = parseInt(secParts[1]) || 0;
                return (min * 60000) + (sec * 1000) + ms;
            }
            const sec = parseInt(parts[1]) || 0;
            return (min * 60000) + (sec * 1000);
        }
        // Handle "M:SS:mmm" with 3 colons
        if (parts.length === 3) {
            const min = parseInt(parts[0]) || 0;
            const sec = parseInt(parts[1]) || 0;
            const ms = parseInt(parts[2]) || 0;
            return (min * 60000) + (sec * 1000) + ms;
        }
        return null;
    }

    /**
     * Format time to MM:SS.mmm
     */
    function formatTime(ms) {
        if (!ms || ms < 0) return '00:00.000';
        const minutes = Math.floor(ms / 60000);
        const seconds = Math.floor((ms % 60000) / 1000);
        const millis = ms % 1000;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${millis.toString().padStart(3, '0')}`;
    }

    /**
     * Update lap times
     */
    function updateLapTimes(data) {
        const laptimeEl = getElement('laptime');
        const timeDiffEl = getElement('timeDiff');
        const bestTimeEl = getElement('bestLap');

        // Current lap time
        if (laptimeEl) {
            if (data.currentTimeStr && data.currentTimeStr !== '') {
                const currentMs = parseTime(data.currentTimeStr);
                if (currentMs !== null) {
                    laptimeEl.textContent = formatTime(currentMs);
                } else {
                    laptimeEl.textContent = data.currentTimeStr;
                }
            } else if (data.iCurrentTime && data.iCurrentTime > 0 && data.iCurrentTime < 2147483647) {
                laptimeEl.textContent = formatTime(data.iCurrentTime);
            } else {
                laptimeEl.textContent = '00:00.000';
            }
        }

        // Time diff
        if (timeDiffEl) {
            const currentMs = data.currentTimeStr ? parseTime(data.currentTimeStr) : null;
            let refMs = data.bestTimeStr ? parseTime(data.bestTimeStr) : null;
            if (!refMs || refMs > 3600000) {
                refMs = data.lastTimeStr ? parseTime(data.lastTimeStr) : null;
            }

            if (currentMs !== null && refMs !== null && currentMs > 0 && refMs > 0 && refMs < 3600000) {
                const diff = currentMs - refMs;
                const sign = diff >= 0 ? '+' : '-';
                timeDiffEl.textContent = sign + formatTime(Math.abs(diff));
            } else {
                timeDiffEl.textContent = '-0.000';
            }
        }

        // Best Lap
        if (bestTimeEl) {
            let bestMs = null;
            if (data.iBestTime && data.iBestTime > 0 && data.iBestTime < 2147483647) {
                bestMs = data.iBestTime;
            } else if (data.bestTimeStr && data.bestTimeStr !== '') {
                bestMs = parseTime(data.bestTimeStr);
            }
            if (!bestMs) {
                if (data.iLastTime && data.iLastTime > 0 && data.iLastTime < 2147483647) {
                    bestMs = data.iLastTime;
                } else if (data.lastTimeStr) {
                    bestMs = parseTime(data.lastTimeStr);
                }
            }

            if (bestMs !== null && bestMs > 0 && bestMs < 3600000) {
                bestTimeEl.textContent = formatTime(bestMs);
            } else {
                bestTimeEl.textContent = '00:00.000';
            }
        }
    }

    /**
     * Update connection status
     */
    function updateStatus(connected) {
        const statusEl = getElement('status');
        if (statusEl) {
            if (connected) {
                statusEl.textContent = 'Connected';
                statusEl.classList.add('connected');
            } else {
                statusEl.textContent = 'Connecting...';
                statusEl.classList.remove('connected');
            }
        }
    }

    /**
     * Handle incoming telemetry message
     */
    function handleMessage(event) {
        try {
            const data = JSON.parse(event.data);

            // Update all displays
            updateRPM(data);
            updateGear(data);
            updateSpeed(data);
            updateABS(data);
            updateTC(data);
            updateDRS(data);
            updatePitLimiter(data);
            updateBrake(data);
            updateFuel(data);
            updateWaterTemp(data);
            updateLap(data);
            updateBrakeBias(data);
            updateTyreType(data);
            updateTyrePressure(data);
            updateTyreTemp(data);
            updateLapTimes(data);

            // Call custom handler if provided
            if (dataHandler) {
                dataHandler(data);
            }
        } catch (e) {
            console.error('[AC Dashboard] Error parsing telemetry data:', e);
        }
    }

    /**
     * Connect to WebSocket server
     */
    function connect() {
        const wsUrl = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws';
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('[AC Dashboard] Connected');
            updateStatus(true);
            if (connectionHandler) connectionHandler(true);
        };

        ws.onclose = () => {
            console.log('[AC Dashboard] Disconnected - Reconnecting...');
            updateStatus(false);
            if (connectionHandler) connectionHandler(false);
            setTimeout(() => {
                // Only reconnect if this is still the current connection
                if (ws && ws.readyState === WebSocket.CLOSED) {
                    connect();
                }
            }, 3000);
        };

        ws.onerror = (error) => {
            console.error('[AC Dashboard] WebSocket error:', error);
        };

        ws.onmessage = handleMessage;
    }

    // Auto-start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => connect());
    } else {
        connect();
    }

    // Export API for advanced customization
    window.ACDashboard = {
        onDataUpdate,
        onConnectionChange,
        parseTime,
        formatTime,
        // Individual update functions
        updateRPM,
        updateGear,
        updateSpeed,
        updateABS,
        updateTC,
        updateDRS,
        updatePitLimiter,
        updateBrake,
        updateFuel,
        updateWaterTemp,
        updateLap,
        updateBrakeBias,
        updateTyreType,
        updateTyrePressure,
        updateTyreTemp,
        updateLapTimes
    };
})();
