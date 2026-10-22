import socket
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import streamlit as st

# Optional auto-refresh dependency:
# Install with: pip install streamlit-autorefresh
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False


# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="NetWatch | Network Analytics",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- SESSION STATE ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None
if "auto_enabled" not in st.session_state:
    st.session_state.auto_enabled = False


# ---------- CUSTOM UI ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%);
    }
    [data-testid="stSidebar"] {
        background: #edf2f8;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #dbe4ee;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);
    }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 2.6rem;
    }
    .hero {
        padding: 1.25rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(110deg, #102a43, #176b87);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 {
        color: white;
        margin-bottom: 0.25rem;
    }
    .hero p {
        color: #e2f3ff;
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- CONNECTION CHECK ----------
def check_connection(host, port, timeout):
    host = host.strip()
    start_time = time.perf_counter()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with socket.create_connection(
            (host, int(port)),
            timeout=float(timeout),
        ):
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "Timestamp": timestamp,
                "Hostname": host,
                "Port": int(port),
                "Status": "Online",
                "Connection Time (ms)": round(elapsed_ms, 2),
                "Details": "TCP connection successful",
            }
    except socket.gaierror:
        message = "Hostname resolution failed"
    except (OSError, TimeoutError) as error:
        message = str(error)
    except Exception as error:
        message = f"Unexpected error: {error}"

    return {
        "Timestamp": timestamp,
        "Hostname": host,
        "Port": int(port),
        "Status": "Failed",
        "Connection Time (ms)": None,
        "Details": message,
    }


def run_checks(hosts, port_value, timeout_value):
    if not hosts:
        return []

    with ThreadPoolExecutor(max_workers=min(5, len(hosts))) as executor:
        return list(
            executor.map(
                lambda hostname: check_connection(
                    hostname, int(port_value), timeout_value
                ),
                hosts,
            )
        )


# ---------- SIDEBAR SETTINGS ----------
st.sidebar.title("🌐 NetWatch")
st.sidebar.caption("Network monitoring & troubleshooting")

hosts_text = st.sidebar.text_area(
    "Hostnames (one per line)",
    value="example.com\npython.org",
    help="Enter up to 10 hostnames that you are authorized to test.",
)
port = st.sidebar.number_input(
    "TCP Port", min_value=1, max_value=65535, value=443, step=1
)
timeout = st.sidebar.slider(
    "Timeout (seconds)", min_value=1, max_value=15, value=5
)

st.sidebar.divider()
st.sidebar.subheader("🔄 Auto-refresh")

auto_enabled = st.sidebar.toggle(
    "Enable automatic checks",
    value=st.session_state.auto_enabled,
    help="Checks the configured hosts repeatedly while this page is open.",
)
st.session_state.auto_enabled = auto_enabled

refresh_interval = st.sidebar.selectbox(
    "Check interval",
    options=[15, 30, 60, 120, 300],
    index=1,
    format_func=lambda seconds: (
        f"{seconds} seconds" if seconds < 60 else f"{seconds // 60} minute(s)"
    ),
    disabled=not auto_enabled,
)

run_button = st.sidebar.button(
    "🔎 Check All Hosts",
    type="primary",
    use_container_width=True,
)

refresh_count = 0
if auto_enabled:
    if AUTOREFRESH_AVAILABLE:
        refresh_count = st_autorefresh(
            interval=int(refresh_interval * 1000),
            key="netwatch_auto_refresh",
        )
    else:
        st.sidebar.warning(
            "Auto-refresh package is missing. Install it using the command shown below."
        )


# ---------- HOST VALIDATION & EXECUTION ----------
hosts = list(
    dict.fromkeys(
        line.strip()
        for line in hosts_text.splitlines()
        if line.strip()
    )
)
should_run = run_button or (
    auto_enabled
    and AUTOREFRESH_AVAILABLE
    and refresh_count > 0
    and (
        st.session_state.last_run is None
        or (datetime.now() - st.session_state.last_run).total_seconds()
        >= refresh_interval
    )
)

if should_run:
    if not hosts:
        st.sidebar.error("Enter at least one hostname.")
    elif len(hosts) > 10:
        st.sidebar.error("Enter no more than 10 hosts per run.")
    else:
        with st.spinner(f"Checking {len(hosts)} host(s)..."):
            new_results = run_checks(hosts, int(port), timeout)
        st.session_state.history.extend(new_results)
        st.session_state.last_run = datetime.now()
        st.sidebar.success(f"Completed {len(new_results)} check(s).")


# ---------- HEADER ----------
st.markdown(
    """
    <div class="hero">
        <h1>🌐 NetWatch</h1>
        <p>NETWORK MONITORING · CONNECTIVITY · ANALYTICS</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write(
    "Check TCP service availability, compare connection times, "
    "review historical results, and export reports."
)
st.info(
    "For systems and services you own or are authorized to test. "
    "This application checks TCP connections; it does not measure packet loss."
)


# ---------- DASHBOARD ----------
st.header("📊 Network Overview")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    total = len(df)
    online = int((df["Status"] == "Online").sum())
    failed = total - online
    success_rate = online / total * 100 if total else 0

    successful_times = pd.to_numeric(
        df.loc[df["Status"] == "Online", "Connection Time (ms)"],
        errors="coerce",
    ).dropna()
    average_time = (
        successful_times.mean() if not successful_times.empty else None
    )

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Total Checks", total)
    metric2.metric("🟢 Online Results", online)
    metric3.metric("🔴 Failed Results", failed)
    metric4.metric("Success Rate", f"{success_rate:.1f}%")

    st.metric(
        "Average TCP Connection Time",
        f"{average_time:.2f} ms" if average_time is not None else "N/A",
    )

    # Status-styled results table
    st.subheader("🖥️ Latest Host Results")
    latest = (
        df.sort_values("Timestamp", ascending=False)
        .drop_duplicates(subset=["Hostname", "Port"], keep="first")
        .copy()
    )

    def status_label(status):
        return "🟢 Online" if status == "Online" else "🔴 Failed"

    display_latest = latest.copy()
    display_latest["Status"] = display_latest["Status"].map(status_label)
    st.dataframe(display_latest, use_container_width=True, hide_index=True)

    # Host summary
    st.subheader("📋 Host Summary")
    summary = df.groupby("Hostname", as_index=False).agg(
        Total_Checks=("Status", "count"),
        Successful_Checks=(
            "Status", lambda values: int((values == "Online").sum())
        ),
        Failed_Checks=(
            "Status", lambda values: int((values == "Failed").sum())
        ),
    )
    summary["Success Rate (%)"] = (
        summary["Successful_Checks"] / summary["Total_Checks"] * 100
    ).round(1)
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # Charts
    left_chart, right_chart = st.columns(2)
    with left_chart:
        st.subheader("📈 Connection Time by Host")
        chart_df = latest[latest["Status"] == "Online"].copy()
        chart_df["Connection Time (ms)"] = pd.to_numeric(
            chart_df["Connection Time (ms)"], errors="coerce"
        )
        chart_df = chart_df.dropna(subset=["Connection Time (ms)"])
        if not chart_df.empty:
            st.bar_chart(
                chart_df.set_index("Hostname")["Connection Time (ms)"]
            )
        else:
            st.info("No successful connection-time measurements yet.")

    with right_chart:
        st.subheader("📊 Online vs Failed")
        status_counts = df["Status"].value_counts().reindex(
            ["Online", "Failed"], fill_value=0
        )
        st.bar_chart(status_counts)

    # History and exports
    st.subheader("🧾 Monitoring History")
    st.dataframe(
        df.sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV Report",
        data=csv_data,
        file_name="netwatch_report.csv",
        mime="text/csv",
    )

    if st.button("🗑️ Clear Monitoring History"):
        st.session_state.history = []
        st.session_state.last_run = None
        st.rerun()
else:
    st.info(
        "No monitoring results yet. Enter hostnames in the sidebar "
        "and click 'Check All Hosts' to start."
    )


# ---------- TROUBLESHOOTING ----------
with st.expander("🛠️ Troubleshooting Guide"):
    st.markdown(
        """
        - **Hostname resolution failed:** Verify the hostname and DNS settings.
        - **Connection timed out:** The service may be slow, blocked, or unreachable.
        - **Connection refused:** The destination may be reachable, but the port is not accepting connections.
        - **Other connection errors:** Check the hostname, port, firewall, and network permissions.
        """
    )

st.caption(
    "Checks are made when requested or on the selected auto-refresh interval. "
    "Connection time is TCP connection establishment time, not full application response time."
)
