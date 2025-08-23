import csv
import io
import streamlit as st

st.title("CSV Processor (Flexible Output)")

def normalize(h: str) -> str:
    return h.replace("\ufeff", "").strip()

def process_csv(file, selected_headers, out_delim="$", use_csv_writer=False):
    text = file.getvalue().decode("utf-8")
    reader = csv.reader(io.StringIO(text), delimiter=";", quotechar="'", escapechar='\\')

    output = io.StringIO()

    try:
        raw_headers = next(reader)
        headers = [normalize(h) for h in raw_headers]
        header_map = {h: i for i, h in enumerate(headers)}

        indices = [header_map[h] for h in selected_headers if h in header_map]

        if use_csv_writer:
            writer = csv.writer(output, delimiter=out_delim, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(selected_headers)
        else:
            output.write(out_delim.join(selected_headers) + "\n")

        for row in reader:
            if not row or all(cell == "" for cell in row):
                continue
            filtered = [row[i] if i < len(row) else "" for i in indices]

            if use_csv_writer:
                writer.writerow(filtered)
            else:
                output.write(out_delim.join(filtered) + "\n")

    except Exception as e:
        st.error(f"Error: {e}")
        return ""

    return output.getvalue()

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
out_delim = st.text_input("Output delimiter", value="$")

if uploaded_file:
    reader = csv.reader(io.StringIO(uploaded_file.getvalue().decode("utf-8")),
                        delimiter=";", quotechar="'", escapechar='\\')
    try:
        raw_headers = next(reader)
        headers = [normalize(h) for h in raw_headers]

        selected = st.multiselect("Select columns to keep", headers, default=headers)

        use_csv_writer = st.checkbox("Use strict CSV writer (adds quotes when needed)", value=False)

        if selected:
            if st.button("Process"):
                result = process_csv(uploaded_file, selected, out_delim=out_delim, use_csv_writer=use_csv_writer)
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
