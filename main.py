import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import re

st.title("CSV Viewer: Select and Visualize Series as Scatter Plot")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

def extract_row_index(label_text):
    match = re.search(r"\[Row (\d+)\]", label_text)
    return int(match.group(1)) if match else None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, header=None)
        st.subheader("Full Data Preview")
        st.dataframe(df)

        st.markdown("---")
        st.subheader("Step 1: Select Label Rows by Content (Column 0)")

        # Prepare label options
        preview_range = min(100, len(df))
        label_options = df.iloc[:preview_range, 0].dropna().astype(str)
        label_dropdown = [f"{label}  [Row {i}]" for i, label in label_options.items()]
        

        start_label = st.selectbox("Select starting row", label_dropdown)
        end_label = st.selectbox("Select ending row", label_dropdown, index=5)

        # Parse selected rows
        start_row = extract_row_index(start_label)
        end_row = extract_row_index(end_label)

        if start_row > end_row:
            st.warning("⚠️ Start row is after end row. Please correct the selection.")
        else:
            labels = df.iloc[start_row:end_row+1, 0].dropna().astype(str).tolist()

            # Columns 14 to 38
            series_cols = list(range(14, 39))
            if df.shape[1] <= max(series_cols):
                st.error("❌ CSV does not contain enough columns (need at least 39).")
                st.stop()

            # Use row 6 for series names
            series_names = df.iloc[6, series_cols].fillna(f"Unnamed").astype(str).tolist()
            col_map = {name: col for name, col in zip(series_names, series_cols)}

            # User selects which series to visualize
            selected_names = st.multiselect("Select series to visualize:", series_names, default=series_names)

            if selected_names:
                data = {}
                for name in selected_names:
                    col = col_map[name]
                    raw = df.iloc[start_row:end_row+1, col].dropna().astype(str)
                    cleaned = raw.str.replace('%', '', regex=False).astype(float)
                    data[name] = cleaned.values

                if len(labels) != len(next(iter(data.values()))):
                    st.warning("⚠️ Label and series lengths mismatch. Cannot plot.")
                else:
                    st.subheader("📊 Scatter Plot")

                    fig, ax = plt.subplots(figsize=(16, 8))  # Bigger figure

                    for name in selected_names:
                        ax.scatter(labels, data[name], label=name)

                    ax.set_xlabel("Label")
                    ax.set_ylabel("Value (%)")
                    ax.set_title("Scatter Plot of Selected Series")
                    plt.xticks(rotation=45, ha='right')

                    # Move legend outside the plot to the right
                    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)

                    st.pyplot(fig)
            else:
                st.info("Please select at least one series to visualize.")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a CSV file to begin.")
