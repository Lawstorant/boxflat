# AC Dashboard Themes

This directory contains custom dashboard themes for the Assetto Corsa web dashboard.

## Creating a Custom Theme

**It's now incredibly simple - just use the right element IDs and everything works automatically!**

1. **Copy the template** - Start by copying `template.html` to a new file (e.g., `mytheme.html`)

2. **Edit the HTML/CSS** - Customize the layout and styling to your liking

3. **Use element IDs** - Add elements with the supported IDs (see below)

4. **Include the script** - Add `<script src="dashboard.js"></script>` before `</body>`

That's it! No JavaScript programming required.

## Supported Element IDs

The universal `dashboard.js` script automatically updates all of these elements:

### Basic Telemetry
- `rpm` - RPM value
- `rpmFill` - RPM bar fill (width 0-100%)
- `gear` - Gear indicator (R, N, 1-7)
- `speed` - Speed in km/h

### Indicators (adds `.active` class when on)
- `abs` - ABS indicator
- `tc` - Traction Control indicator
- `drs` - DRS indicator
- `pitLimiter` - Pit Limiter indicator (adds `.danger` class)

### Value Displays (shows numeric/ON-OFF state)
- `absValue` / `absText` - ABS value or text
- `tcValue` / `tcText` - TC value or text
- `drsValue` / `drsText` / `dimValue` - DRS state
- `pitValue` / `pitText` / `athValue` - Pit limiter state

### Icon Visibility (toggles `.hidden` class)
- `icon-brake` - Brake icon
- `icon-hazard` - Hazard/warning icon
- `icon-high` - High beam icon
- `icon-low` - Low beam icon

### Fuel
- `fuelFill` - Fuel bar (width 0-100%)
- `fuelRem` - Remaining fuel in liters
- `fuelPerLap` - Fuel per lap in liters
- `fuelCap` - Fuel capacity in liters

### Tyre Data
- `tyreFLPressure`, `tyreFRPressure`, `tyreRLPressure`, `tyreRRPressure` - Tyre pressures
- `tyreFLTemp`, `tyreFRTemp`, `tyreRLTemp`, `tyreRRTemp` - Tyre temperatures
- `tyreType` - Tyre compound (DRY/WET)

### Lap Data
- `lap` - Current lap number
- `laptime` - Current lap time (MM:SS.mmm)
- `timeDiff` - Time difference from best/last lap
- `bestLap` - Best lap time

### Other
- `waterTemp` - Water temperature in °C
- `brakeBias` - Brake bias percentage
- `status` - Connection status (adds `.connected` class)

## Example Minimal Theme

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #000; color: #fff; font-family: Arial; }
        .active { background: #0f0; }
        .danger { background: #f00; }
    </style>
</head>
<body>
    <div id="speed">0</div>
    <div id="gear">N</div>
    <div id="rpm">0</div>
    <div id="abs" class="indicator">ABS</div>
    <div id="tc" class="indicator">TC</div>
    <div id="fuelRem">-</div>
    <script src="dashboard.js"></script>
</body>
</html>
```

That's all you need - it just works!

## Advanced Customization (Optional)

If you need custom behavior beyond the automatic updates, you can use the JavaScript API:

```html
<script src="dashboard.js"></script>
<script>
    // Optional: Custom data handler
    ACDashboard.onDataUpdate((data) => {
        console.log('Custom logic here', data);
    });

    // Optional: Connection state handler
    ACDashboard.onConnectionChange((connected) => {
        console.log('Connected:', connected);
    });
</script>
```

## Loading Your Theme

1. Save your theme as an `.html` file in this directory
2. The theme name will be the filename without `.html`, capitalized (e.g., `mytheme.html` → `Mytheme`)
3. Select your theme from the Dashboard Theme dropdown in Boxflat settings
4. The dashboard will automatically reload with your new theme

## Tips

- Keep your CSS efficient - the dashboard updates at ~60 FPS
- Use CSS transitions for smooth animations
- Test on different screen sizes (phone, tablet, PC)
- You can test themes by adding `?theme=ThemeName` to the dashboard URL
- The `dashboard.js` script handles automatic reconnection if the connection drops

## Available Themes

- `default.html` - Clean, modern dark theme
- `porsche.html` - Porsche-style dashboard with comprehensive telemetry
- `template.html` - Full-featured template showing all available elements
