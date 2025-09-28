# Create a comprehensive Telegram Terminal Bot architecture flowchart
diagram_code = """
flowchart TD
    %% User Interface Components
    TelegramApp("Telegram App")
    
    %% External Services
    TelegramAPI(("Telegram API"))
    
    %% Core Bot Components
    BotMain["Bot Main Script"]
    MessageParser["Message Parser"]
    CommandExec["Command Executor"]
    FileHandler["File Handler"]
    SessionMgr["Session Manager"]
    
    %% Security Components
    Auth{{Authorization}}
    
    %% System Services
    SysMonitor{System Monitor}
    SystemdSvc{Systemd Service}
    ScreenTool{Screenshot Tool}
    AudioCtrl{Audio Control}
    BrightCtrl{Brightness Control}
    LinuxShell{Linux Shell}
    NetMonitor{Network Monitor}
    BattMonitor{Battery Monitor}
    
    %% Data Storage
    ConfigFile[("Config File")]
    LogFiles[("Log Files")]
    TempStorage[("Temp Storage")]
    
    %% Data Flow Connections
    TelegramApp -->|User Messages| TelegramAPI
    TelegramAPI -->|API Updates| BotMain
    BotMain -->|Verify User| Auth
    Auth -->|Authorized| MessageParser
    MessageParser -->|Commands| CommandExec
    MessageParser -->|Files| FileHandler
    CommandExec -->|Shell Commands| LinuxShell
    CommandExec -->|Screenshot| ScreenTool
    CommandExec -->|Volume| AudioCtrl
    CommandExec -->|Brightness| BrightCtrl
    SessionMgr -->|Session Data| TempStorage
    SysMonitor -->|Alerts| BotMain
    NetMonitor -->|Status| SysMonitor
    BattMonitor -->|Status| SysMonitor
    BotMain -->|Activity Logs| LogFiles
    ConfigFile -->|User IDs| Auth
    SystemdSvc -->|Auto Start| BotMain
    
    %% Styling
    classDef userInterface fill:#B3E5EC,stroke:#1FB8CD,stroke-width:2px
    classDef externalService fill:#FFCDD2,stroke:#DB4545,stroke-width:2px
    classDef coreComponent fill:#A5D6A7,stroke:#2E8B57,stroke-width:2px
    classDef security fill:#FFCDD2,stroke:#DB4545,stroke-width:3px
    classDef systemService fill:#FFEB8A,stroke:#D2BA4C,stroke-width:2px
    classDef dataStorage fill:#E0E0E0,stroke:#666666,stroke-width:2px
    
    class TelegramApp userInterface
    class TelegramAPI externalService
    class BotMain,MessageParser,CommandExec,FileHandler,SessionMgr coreComponent
    class Auth security
    class SysMonitor,SystemdSvc,ScreenTool,AudioCtrl,BrightCtrl,LinuxShell,NetMonitor,BattMonitor systemService
    class ConfigFile,LogFiles,TempStorage dataStorage
"""

# Create the mermaid diagram with both PNG and SVG outputs
png_path, svg_path = create_mermaid_diagram(
    diagram_code, 
    png_filepath='telegram_bot_architecture.png',
    svg_filepath='telegram_bot_architecture.svg',
    width=1400,
    height=1000
)

print(f"Flowchart saved as PNG: {png_path}")
print(f"Flowchart saved as SVG: {svg_path}")