import csv
import io
import streamlit as st

st.title("CSV Processor (Strict CSV Writer)")

def normalize(h: str) -> str:
    return h.replace("\ufeff", "").strip()

def process_csv(file, selected_headers, out_delim="$"):
    text = file.getvalue().decode("utf-8")
    reader = csv.reader(io.StringIO(text), delimiter=";", quotechar="'", escapechar='\\')

    output = io.StringIO()
    writer = csv.writer(
        output,
        delimiter=out_delim,
        quotechar='"',          # standard double quotes
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n"
    )

    try:
        raw_headers = next(reader)
        headers = [normalize(h) for h in raw_headers]
        header_map = {h: i for i, h in enumerate(headers)}

        indices = [header_map[h] for h in selected_headers if h in header_map]

        # Write header row
        writer.writerow(selected_headers)

        for row in reader:
            if not row or all(cell == "" for cell in row):
                continue
            filtered = [row[i] if i < len(row) else "" for i in indices]
            writer.writerow(filtered)

    except Exception as e:
        st.error(f"Error: {e}")
        return ""

    return output.getvalue()

# --- Streamlit UI ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
out_delim = st.text_input("Output delimiter", value="$")

if uploaded_file:
    # Read headers
    reader = csv.reader(io.StringIO(uploaded_file.getvalue().decode("utf-8")),
                        delimiter=";", quotechar="'", escapechar='\\')
    try:
        raw_headers = next(reader)
        headers = [normalize(h) for h in raw_headers]

        selected = st.multiselect("Select columns to keep", headers, default=headers)

        if selected:
            if st.button("Process"):
                result = process_csv(uploaded_file, selected, out_delim=out_delim)
                if result:
                    st.text("Preview:")
                    st.text("\n".join(result.splitlines()[:10]))

                    st.download_button(
                        "Download processed CSV",
                        data=result,
                        file_name="filtered_export.csv",
                        mime="text/csv"
                    )
    except Exception as e:
        st.error(f"Could not read headers: {e}")
