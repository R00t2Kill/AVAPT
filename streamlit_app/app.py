import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# =============================
# 🌟 PAGE CONFIG
# =============================
st.set_page_config(
    page_title="AVAPT Intelligence Hub",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# 🎨 CUSTOM CSS FOR FIRE DESIGN
# =============================
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Glassmorphism cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        transition: all 0.3s ease;
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.3);
    }
    
    /* Animated gradient text */
    .gradient-text {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 3s ease infinite;
        font-weight: 800;
        font-size: 3rem;
    }
    
    @keyframes gradient {
        0% {background-position: 0% center;}
        50% {background-position: 100% center;}
        100% {background-position: 0% center;}
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-online {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .status-alert {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    @keyframes pulse {
        0%, 100% {opacity: 1;}
        50% {opacity: 0.7;}
    }
    
    /* Modern sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: #e0e7ff !important;
        font-weight: 600;
    }
    
    /* Neon glow effects */
    .neon-box {
        border: 2px solid #6366f1;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4),
                    inset 0 0 20px rgba(99, 102, 241, 0.1);
        animation: neon-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes neon-glow {
        from {box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);}
        to {box-shadow: 0 0 30px rgba(99, 102, 241, 0.8);}
    }
    
    /* Custom metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Alert box */
    .alert-box {
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid;
        animation: slideInRight 0.5s ease;
    }
    
    @keyframes slideInRight {
        from {transform: translateX(50px); opacity: 0;}
        to {transform: translateX(0); opacity: 1;}
    }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
        color: #fee2e2;
    }
    
    .alert-warning {
        background: rgba(245, 158, 11, 0.1);
        border-color: #f59e0b;
        color: #fef3c7;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 4px solid rgba(99, 102, 241, 0.1);
        border-top: 4px solid #6366f1;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% {transform: rotate(0deg);}
        100% {transform: rotate(360deg);}
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 🧭 ENHANCED SIDEBAR
# =============================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <div style='font-size: 4rem; margin-bottom: 10px;'>🔮</div>
            <h1 style='color: #e0e7ff; margin: 0; font-size: 1.8rem;'>AVAPT</h1>
            <p style='color: #a5b4fc; margin: 5px 0; font-size: 0.9rem;'>Intelligence Hub</p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    page = st.radio(
        "🧭 Navigation",
        ["🏠 Command Center", "🧠 Neural Health", "📡 Live Feed", "📊 Deep Analytics", "🌐 Global Map", "⚡ System Control"],
        label_visibility="visible"
    )

    st.divider()
    
    # Enhanced settings
    st.markdown("### ⚙️ Configuration")
    refresh_rate = st.slider("🔄 Refresh Interval (s)", 5, 60, 10)
    theme_mode = st.selectbox("🎨 Theme", ["Cyber Dark", "Neon Blue", "Matrix Green"])
    show_animations = st.checkbox("✨ Animations", value=True)
    
    st.divider()
    
    # Connection status
    st.markdown("""
        <div style='background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #10b981;'>
            <div style='color: #10b981; font-weight: 600; margin-bottom: 5px;'>⚡ SYSTEM STATUS</div>
            <div style='color: #6ee7b7; font-size: 0.85rem;'>All systems operational</div>
        </div>
    """, unsafe_allow_html=True)

# =============================
# 🔌 BACKEND API CONFIG
# =============================
BACKEND_URL = st.secrets.get("backend_url", "http://127.0.0.1:8000")

def get_health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"status": "unreachable"}

def get_devices(size=50):
    try:
        r = requests.get(f"{BACKEND_URL}/api/devices?size={size}", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

# =============================
# 🏠 COMMAND CENTER
# =============================
if page == "🏠 Command Center":
    # Animated header
    st.markdown('<h1 class="gradient-text">⚡ COMMAND CENTER</h1>', unsafe_allow_html=True)
    st.caption(f"🕐 Real-time Intelligence | {datetime.now().strftime('%A, %B %d, %Y • %H:%M:%S')}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate realistic data
    active_cameras = random.randint(28, 35)
    total_cameras = 35
    alerts = random.randint(2, 8)
    uptime = round(random.uniform(99.2, 99.97), 2)
    bandwidth = round(random.uniform(450, 890), 1)
    
    # Hero metrics with custom styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; margin-bottom: 10px;'>📹</div>
                <div style='font-size: 2.8rem; font-weight: 800; color: #6366f1;'>{active_cameras}/{total_cameras}</div>
                <div style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem;'>Active Cameras</div>
                <div style='margin-top: 10px;'>
                    <span class='status-badge status-online'>● ONLINE</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        alert_color = "#ef4444" if alerts > 5 else "#f59e0b"
        st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; margin-bottom: 10px;'>🚨</div>
                <div style='font-size: 2.8rem; font-weight: 800; color: {alert_color};'>{alerts}</div>
                <div style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem;'>Active Alerts</div>
                <div style='margin-top: 10px;'>
                    <span class='status-badge status-{"alert" if alerts > 5 else "warning"}'>⚠ {"CRITICAL" if alerts > 5 else "MODERATE"}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; margin-bottom: 10px;'>⚡</div>
                <div style='font-size: 2.8rem; font-weight: 800; color: #10b981;'>{uptime}%</div>
                <div style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem;'>System Uptime</div>
                <div style='margin-top: 10px;'>
                    <span class='status-badge status-online'>● STABLE</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 2.5rem; margin-bottom: 10px;'>🌐</div>
                <div style='font-size: 2.8rem; font-weight: 800; color: #8b5cf6;'>{bandwidth}</div>
                <div style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem;'>Bandwidth (Mbps)</div>
                <div style='margin-top: 10px;'>
                    <span class='status-badge status-online'>● OPTIMAL</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Real-time monitoring charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Network Activity Stream")
        
        # Generate time series data
        time_points = pd.date_range(end=datetime.now(), periods=30, freq='1min')
        camera_data = [random.randint(20, 35) for _ in range(30)]
        bandwidth_data = [random.randint(400, 900) for _ in range(30)]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=time_points, y=camera_data, name="Active Cameras", 
                      line=dict(color='#6366f1', width=3),
                      fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=time_points, y=bandwidth_data, name="Bandwidth (Mbps)",
                      line=dict(color='#8b5cf6', width=3, dash='dot')),
            secondary_y=True
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=350,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Alert Distribution")
        
        alert_types = ['Motion', 'Tampering', 'Connection', 'Quality', 'Other']
        alert_counts = [random.randint(0, 5) for _ in range(5)]
        colors = ['#ef4444', '#f59e0b', '#6366f1', '#8b5cf6', '#ec4899']
        
        fig = go.Figure(data=[go.Pie(
            labels=alert_types,
            values=alert_counts,
            hole=0.6,
            marker=dict(colors=colors),
            textposition='auto',
            textfont=dict(size=14, color='white')
        )])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=350,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Live alerts feed
    st.markdown("### 🔴 Live Alert Feed")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        alert_messages = [
            ("CRITICAL", "Camera 12 - Motion detected in restricted area", "2 min ago"),
            ("WARNING", "Camera 5 - Frame rate dropped below threshold", "5 min ago"),
            ("INFO", "Camera 8 - Successfully reconnected", "8 min ago"),
            ("WARNING", "Camera 3 - High latency detected (180ms)", "12 min ago"),
            ("CRITICAL", "Camera 15 - Possible tampering detected", "15 min ago"),
        ]
        
        for severity, message, time_ago in alert_messages[:4]:
            alert_class = "alert-critical" if severity == "CRITICAL" else "alert-warning"
            icon = "🔴" if severity == "CRITICAL" else "⚠️" if severity == "WARNING" else "ℹ️"
            st.markdown(f"""
                <div class='alert-box {alert_class}'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 700;'>{icon} {severity}</span> • {message}
                        </div>
                        <div style='opacity: 0.7; font-size: 0.85rem;'>{time_ago}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎛️ Quick Actions")
        
        if st.button("🔄 Refresh All Streams", use_container_width=True):
            st.success("Refreshing all camera streams...")
        
        if st.button("🚨 Acknowledge Alerts", use_container_width=True):
            st.info("Alerts acknowledged")
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Generating system report...")
        
        if st.button("🔧 System Diagnostics", use_container_width=True):
            st.info("Running diagnostics...")

# =============================
# 🧠 NEURAL HEALTH
# =============================
elif page == "🧠 Neural Health":
    st.markdown('<h1 class="gradient-text">🧠 SYSTEM NEURAL HEALTH</h1>', unsafe_allow_html=True)
    
    health = get_health()
    
    # System status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "OPTIMAL" if health.get("status") == "ok" else "DEGRADED"
        color = "#10b981" if status == "OPTIMAL" else "#ef4444"
        st.markdown(f"""
            <div class='neon-box' style='border-color: {color}; text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>{"✅" if status == "OPTIMAL" else "⚠️"}</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: {color};'>{status}</div>
                <div style='color: #94a3b8; margin-top: 5px;'>Backend Status</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cpu_usage = random.randint(35, 75)
        cpu_color = "#10b981" if cpu_usage < 60 else "#f59e0b" if cpu_usage < 80 else "#ef4444"
        st.markdown(f"""
            <div class='neon-box' style='border-color: {cpu_color}; text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>⚡</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: {cpu_color};'>{cpu_usage}%</div>
                <div style='color: #94a3b8; margin-top: 5px;'>CPU Load</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        mem_used = round(random.uniform(2.1, 6.5), 1)
        mem_total = 8.0
        mem_pct = int((mem_used / mem_total) * 100)
        mem_color = "#10b981" if mem_pct < 70 else "#f59e0b" if mem_pct < 85 else "#ef4444"
        st.markdown(f"""
            <div class='neon-box' style='border-color: {mem_color}; text-align: center;'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>💾</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: {mem_color};'>{mem_used}GB</div>
                <div style='color: #94a3b8; margin-top: 5px;'>Memory Usage / {mem_total}GB</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Resource monitoring
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 CPU Performance")
        
        time_points = list(range(60))
        cpu_history = [random.randint(30, 80) for _ in range(60)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_points, y=cpu_history,
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.3)',
            line=dict(color='#6366f1', width=3),
            name='CPU %'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=300,
            xaxis_title="Time (s)",
            yaxis_title="Usage %",
            hovermode='x'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)', range=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💿 Memory Utilization")
        
        mem_history = [round(random.uniform(2.0, 6.5), 1) for _ in range(60)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_points, y=mem_history,
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.3)',
            line=dict(color='#8b5cf6', width=3),
            name='Memory (GB)'
        ))
        
        fig.add_hline(y=8.0, line_dash="dash", line_color="#ef4444", annotation_text="Max Capacity")
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=300,
            xaxis_title="Time (s)",
            yaxis_title="Memory (GB)",
            hovermode='x'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(139, 92, 246, 0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(139, 92, 246, 0.1)', range=[0, 10])
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Network statistics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        ("🌐", "Network I/O", f"{random.randint(450, 950)} Mbps", "#6366f1"),
        ("📡", "Latency", f"{random.randint(15, 45)} ms", "#8b5cf6"),
        ("🔄", "Uptime", f"{random.randint(168, 720)}h {random.randint(10, 59)}m", "#10b981"),
        ("💾", "Disk I/O", f"{random.randint(120, 450)} MB/s", "#ec4899"),
    ]
    
    for col, (icon, label, value, color) in zip([col1, col2, col3, col4], metrics_data):
        with col:
            st.markdown(f"""
                <div style='background: rgba(99, 102, 241, 0.05); padding: 20px; border-radius: 15px; border: 1px solid {color}; text-align: center;'>
                    <div style='font-size: 2.5rem;'>{icon}</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: {color}; margin: 10px 0;'>{value}</div>
                    <div style='color: #94a3b8; font-size: 0.9rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)

# =============================
# 📡 LIVE FEED
# =============================
elif page == "📡 Live Feed":
    st.markdown('<h1 class="gradient-text">📡 LIVE SYSTEM FEED</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📜 Real-Time Event Log")
        
        log_entries = [
            ("INFO", "System initialized successfully", "just now", "#6366f1"),
            ("SUCCESS", "Camera 12 stream connected", "1 min ago", "#10b981"),
            ("INFO", "Health check passed", "2 min ago", "#6366f1"),
            ("WARNING", "Camera 5 experiencing high latency", "3 min ago", "#f59e0b"),
            ("SUCCESS", "Analytics module loaded", "5 min ago", "#10b981"),
            ("ALERT", "Motion detected in Zone A - Camera 8", "7 min ago", "#ef4444"),
            ("INFO", "Database backup completed", "10 min ago", "#6366f1"),
            ("WARNING", "Frame drop detected on Camera 3", "12 min ago", "#f59e0b"),
            ("SUCCESS", "Network optimization applied", "15 min ago", "#10b981"),
            ("INFO", "Scheduled maintenance reminder", "18 min ago", "#6366f1"),
        ]
        
        for log_type, message, time_ago, color in log_entries:
            st.markdown(f"""
                <div style='background: rgba(99, 102, 241, 0.05); padding: 15px 20px; border-radius: 10px; margin: 8px 0; border-left: 4px solid {color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='color: {color}; font-weight: 700; margin-right: 10px;'>[{log_type}]</span>
                            <span style='color: #e0e7ff;'>{message}</span>
                        </div>
                        <span style='color: #94a3b8; font-size: 0.85rem;'>{time_ago}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Event Statistics")
        
        event_counts = {
            'INFO': random.randint(120, 200),
            'SUCCESS': random.randint(80, 150),
            'WARNING': random.randint(10, 40),
            'ALERT': random.randint(5, 15)
        }
        
        colors_map = {'INFO': '#6366f1', 'SUCCESS': '#10b981', 'WARNING': '#f59e0b', 'ALERT': '#ef4444'}
        
        fig = go.Figure(data=[go.Bar(
            x=list(event_counts.values()),
            y=list(event_counts.keys()),
            orientation='h',
            marker=dict(color=[colors_map[k] for k in event_counts.keys()]),
            text=list(event_counts.values()),
            textposition='auto',
        )])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=300,
            xaxis_title="Count",
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🔥 Activity Heatmap")
        st.markdown(f"""
            <div style='background: rgba(99, 102, 241, 0.1); padding: 15px; border-radius: 10px; text-align: center;'>
                <div style='color: #e0e7ff; font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;'>Last Hour</div>
                <div style='color: #6366f1; font-size: 2.5rem; font-weight: 800;'>{sum(event_counts.values())}</div>
                <div style='color: #94a3b8; margin-top: 5px;'>Total Events</div>
            </div>
        """, unsafe_allow_html=True)

# =============================
# 📊 DEEP ANALYTICS
# =============================
elif page == "📊 Deep Analytics":
    st.markdown('<h1 class="gradient-text">📊 DEEP ANALYTICS</h1>', unsafe_allow_html=True)
    st.caption("Advanced performance metrics and predictive insights")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Camera performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎥 Camera Performance Matrix")
        
        cameras = [f"CAM-{i:02d}" for i in range(1, 11)]
        fps_data = [random.randint(18, 30) for _ in range(10)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=cameras,
            y=fps_data,
            marker=dict(
                color=fps_data,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="FPS")
            ),
            text=fps_data,
            textposition='auto',
        ))
        
        fig.add_hline(y=24, line_dash="dash", line_color="#10b981", annotation_text="Target FPS")
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=350,
            xaxis_title="Camera ID",
            yaxis_title="Frames Per Second",
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⚡ Network Latency Analysis")
        
        latency_data = [random.randint(25, 150) for _ in range(10)]
        
        fig = go.Figure()
        
        colors = ['#10b981' if x < 50 else '#f59e0b' if x < 100 else '#ef4444' for x in latency_data]
        
        fig.add_trace(go.Bar(
            x=cameras,
            y=latency_data,
            marker=dict(color=colors),
            text=[f"{x}ms" for x in latency_data],
            textposition='auto',
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=350,
            xaxis_title="Camera ID",
            yaxis_title="Latency (ms)",
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Advanced analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 24-Hour Trend Analysis")
        
        hours = list(range(24))
        activity = [random.randint(10, 100) for _ in range(24)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=activity,
            mode='lines+markers',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=8, color='#8b5cf6'),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.2)',
            name='Activity Level'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=300,
            xaxis_title="Hour of Day",
            yaxis_title="Activity Score",
            hovermode='x'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(99, 102, 241, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Detection Accuracy Metrics")
        
        detection_types = ['Motion', 'Face', 'Vehicle', 'Object', 'Crowd']
        accuracy = [random.randint(85, 99) for _ in range(5)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=accuracy,
            theta=detection_types,
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.3)',
            line=dict(color='#6366f1', width=2),
            marker=dict(size=8, color='#8b5cf6')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(99, 102, 241, 0.2)'
                ),
                angularaxis=dict(gridcolor='rgba(99, 102, 241, 0.2)')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e7ff'),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance scores
    st.markdown("### 🏆 System Performance Scores")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    scores = [
        ("🎯", "Accuracy", random.randint(92, 99), "#10b981"),
        ("⚡", "Speed", random.randint(88, 97), "#6366f1"),
        ("🛡️", "Reliability", random.randint(95, 99), "#8b5cf6"),
        ("🔍", "Detection", random.randint(90, 98), "#ec4899"),
        ("📡", "Connectivity", random.randint(93, 99), "#f59e0b")
    ]
    
    for col, (icon, label, score, color) in zip([col1, col2, col3, col4, col5], scores):
        with col:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); 
                            padding: 25px; border-radius: 15px; text-align: center; border: 2px solid {color};'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>{icon}</div>
                    <div style='font-size: 2.5rem; font-weight: 800; color: {color};'>{score}%</div>
                    <div style='color: #94a3b8; margin-top: 5px; font-size: 0.9rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)

# =============================
# 🌐 GLOBAL MAP
# =============================
elif page == "🌐 Global Map":
    st.markdown('<h1 class="gradient-text">🌐 GLOBAL DEVICE MAP</h1>', unsafe_allow_html=True)
    st.caption("Real-time geospatial visualization of all connected devices")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate sample data for demo (always show something)
    sample_locations = [
        (26.8467, 80.9462, "CAM-HQ-01", "Headquarters"),
        (26.8500, 80.9500, "CAM-SEC-02", "Security Gate"),
        (26.8400, 80.9400, "CAM-PAR-03", "Parking Lot"),
        (26.8550, 80.9600, "CAM-WAR-04", "Warehouse"),
        (26.8350, 80.9350, "CAM-ENT-05", "Main Entrance"),
        (28.7041, 77.1025, "CAM-DL-01", "Delhi Office"),
        (19.0760, 72.8777, "CAM-MB-01", "Mumbai Branch"),
        (12.9716, 77.5946, "CAM-BG-01", "Bangalore Center"),
        (13.0827, 80.2707, "CAM-CH-01", "Chennai Hub"),
        (22.5726, 88.3639, "CAM-KL-01", "Kolkata Station"),
        (17.3850, 78.4867, "CAM-HY-01", "Hyderabad Hub"),
        (23.0225, 72.5714, "CAM-AH-01", "Ahmedabad Center"),
    ]
    
    # Always use sample data for demo
    data_list = []
    for lat, lon, device_id, location in sample_locations:
        # Add some random variation
        lat_var = lat + random.uniform(-0.01, 0.01)
        lon_var = lon + random.uniform(-0.01, 0.01)
        status = random.choice(["online", "online", "online", "online", "warning"])
        data_list.append({
            "lat": lat_var,
            "lon": lon_var,
            "device": device_id,
            "location": location,
            "status": status
        })
    
    data = pd.DataFrame(data_list)
    
    # Status summary
    col1, col2, col3, col4 = st.columns(4)
    
    online_count = len(data[data['status'] == 'online'])
    warning_count = len(data[data['status'] == 'warning'])
    total_devices = len(data)
    
    with col1:
        st.markdown(f"""
            <div style='background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #10b981; text-align: center;'>
                <div style='font-size: 2.5rem; color: #10b981; font-weight: 800;'>{online_count}</div>
                <div style='color: #94a3b8; margin-top: 5px;'>● Online Devices</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: rgba(245, 158, 11, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #f59e0b; text-align: center;'>
                <div style='font-size: 2.5rem; color: #f59e0b; font-weight: 800;'>{warning_count}</div>
                <div style='color: #94a3b8; margin-top: 5px;'>⚠ Warning Status</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #6366f1; text-align: center;'>
                <div style='font-size: 2.5rem; color: #6366f1; font-weight: 800;'>{total_devices}</div>
                <div style='color: #94a3b8; margin-top: 5px;'>📍 Total Locations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        uptime_pct = round(random.uniform(98.5, 99.9), 2)
        st.markdown(f"""
            <div style='background: rgba(139, 92, 246, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #8b5cf6; text-align: center;'>
                <div style='font-size: 2.5rem; color: #8b5cf6; font-weight: 800;'>{uptime_pct}%</div>
                <div style='color: #94a3b8; margin-top: 5px;'>⚡ Network Uptime</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive map - Now data is always populated
    # Create color coding based on status
    def get_color(status):
        if status == 'online':
            return [16, 185, 129, 200]
        elif status == 'warning':
            return [245, 158, 11, 200]
        else:
            return [239, 68, 68, 200]
    
    data['color'] = data['status'].apply(get_color)
    
    view_state = pdk.ViewState(
        latitude=data["lat"].mean(),
        longitude=data["lon"].mean(),
        zoom=5,
        pitch=45,
        bearing=0
    )
    
    # Scatterplot layer for devices
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position='[lon, lat]',
        get_color='color',
        get_radius=30000,
        pickable=True,
        auto_highlight=True,
    )
    
    # Column layer for 3D effect
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position='[lon, lat]',
        get_elevation=50000,
        elevation_scale=1,
        radius=20000,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )
    
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v11",
        initial_view_state=view_state,
        layers=[column_layer, scatter_layer],
        tooltip={
            "html": "<b>Device:</b> {device}<br/><b>Location:</b> {location}<br/><b>Status:</b> {status}",
            "style": {
                "backgroundColor": "rgba(30, 27, 75, 0.95)",
                "color": "white",
                "border": "2px solid #6366f1",
                "borderRadius": "8px",
                "padding": "10px"
            }
        },
    )
    
    st.pydeck_chart(deck)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Device list
    st.markdown("### 📋 Device Registry")
    
    display_data = data[['device', 'location', 'status', 'lat', 'lon']].copy()
    display_data.columns = ['Device ID', 'Location', 'Status', 'Latitude', 'Longitude']
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# =============================
# ⚡ SYSTEM CONTROL
# =============================
elif page == "⚡ System Control":
    st.markdown('<h1 class="gradient-text">⚡ SYSTEM CONTROL CENTER</h1>', unsafe_allow_html=True)
    st.caption("Advanced system configuration and management")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎛️ Camera Management")
        
        # Camera control interface
        cameras_list = [f"Camera {i:02d}" for i in range(1, 16)]
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            selected_camera = st.selectbox("Select Camera", cameras_list)
        
        with col_b:
            action = st.selectbox("Action", ["Start Stream", "Stop Stream", "Restart", "Configure"])
        
        with col_c:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Execute", use_container_width=True, type="primary"):
                st.success(f"✅ {action} executed on {selected_camera}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bulk operations
        st.markdown("### 🔄 Bulk Operations")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔄 Restart All Cameras", use_container_width=True):
                with st.spinner("Restarting all cameras..."):
                    time.sleep(1)
                st.success("All cameras restarted successfully!")
        
        with col_b:
            if st.button("🧹 Clear All Alerts", use_container_width=True):
                st.success("All alerts cleared!")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📊 Export System Report", use_container_width=True):
                st.info("Generating comprehensive system report...")
        
        with col_b:
            if st.button("🔧 Run Diagnostics", use_container_width=True):
                with st.spinner("Running system diagnostics..."):
                    time.sleep(1.5)
                st.success("Diagnostics completed. All systems nominal.")
    
    with col2:
        st.markdown("### ⚙️ System Settings")
        
        st.markdown("**🎥 Video Quality**")
        quality = st.select_slider(
            "Resolution",
            options=["480p", "720p", "1080p", "4K"],
            value="1080p",
            label_visibility="collapsed"
        )
        
        st.markdown("**🔔 Alert Threshold**")
        alert_sensitivity = st.slider(
            "Sensitivity",
            0, 100, 75,
            label_visibility="collapsed"
        )
        
        st.markdown("**💾 Storage Management**")
        retention = st.number_input(
            "Retention Days",
            min_value=1,
            max_value=90,
            value=30,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 Save Settings", use_container_width=True, type="primary"):
            st.success("Settings saved successfully!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System maintenance
    st.markdown("### 🛠️ System Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #6366f1;'>
                <h4 style='color: #6366f1; margin-top: 0;'>🗄️ Database</h4>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Last backup: 2 hours ago</p>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Size: 2.4 GB</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Backup Now", use_container_width=True):
            st.info("Database backup initiated...")
    
    with col2:
        st.markdown("""
            <div style='background: rgba(139, 92, 246, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #8b5cf6;'>
                <h4 style='color: #8b5cf6; margin-top: 0;'>🔄 Updates</h4>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Current: v2.4.1</p>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Latest: v2.4.2</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Check Updates", use_container_width=True):
            st.success("System is up to date!")
    
    with col3:
        st.markdown("""
            <div style='background: rgba(236, 72, 153, 0.1); padding: 20px; border-radius: 12px; border: 2px solid #ec4899;'>
                <h4 style='color: #ec4899; margin-top: 0;'>🧹 Cleanup</h4>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Temp files: 1.2 GB</p>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Old logs: 850 MB</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Clean Up", use_container_width=True):
            st.success("Cleanup completed!")

# =============================
# ⏳ AUTO REFRESH (Footer info)
# =============================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 20px;'>
        🔄 Auto-refresh: Every {refresh_rate}s | Last updated: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)