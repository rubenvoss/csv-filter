import csv
import io
import streamlit as st
import pandas as pd

def process_and_filter_csv(
    input_file,
    selected_headers,
    input_delimiter: str = ";",
    output_delimiter: str = "$"
) -> str:
    """
    Reads a CSV file with given input_delimiter, converts it
    to output_delimiter, and returns a string of the filtered CSV content.
    """
    def normalize(h: str) -> str:
        return h.replace("\ufeff", "").strip()  # remove BOM + trim spaces

    output = io.StringIO()
    reader = csv.reader(io.StringIO(input_file.getvalue().decode("utf-8")),
                        delimiter=input_delimiter, quotechar="'", escapechar='\\')

    try:
        # Read and normalize header row
        raw_headers = next(reader)
        headers = [normalize(h) for h in raw_headers]
        header_map = {h: i for i, h in enumerate(headers)}

        indices = [header_map[h] for h in selected_headers if h in header_map]
        synth_count = len(selected_headers) - len(indices)
        max_index_needed = max(indices) if indices else -1

        # Write the filtered headers
        output.write(output_delimiter.join(selected_headers) + "\n")

        for row in reader:
            if not row or all(cell == "" for cell in row):
                continue  # skip blank rows

            # Pad short rows
            if len(row) <= max_index_needed:
                row += [""] * (max_index_needed + 1 - len(row))

            filtered_row = [row[i] for i in indices]
            if synth_count:
                filtered_row += [""] * synth_count

            output.write(output_delimiter.join(filtered_row) + "\n")

    except StopIteration:
        st.error("Error: Input file appears empty or missing a header row.")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""

    return output.getvalue()


# Streamlit App
st.title("CSV Processor & Filter")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Input delimiter selection
    st.subheader("Delimiter Settings")
    input_delimiter = st.selectbox(
        "Input delimiter",
        options=[",", ";", "|", "tab", "other"],
        index=1  # default ";"
    )
    if input_delimiter == "tab":
        input_delimiter = "\t"
    elif input_delimiter == "other":
        input_delimiter = st.text_input("Enter custom input delimiter", value=";")

    output_delimiter = st.text_input("Output delimiter", value="$")

    # Read headers from file
    reader = csv.reader(io.StringIO(uploaded_file.getvalue().decode("utf-8")),
                        delimiter=input_delimiter, quotechar="'", escapechar='\\')
    try:
        raw_headers = next(reader)
        headers = [h.replace("\ufeff", "").strip() for h in raw_headers]

        # Let user pick headers
        selected_headers = st.multiselect(
            "Select columns to keep in the output",
            headers,
            default=headers  # default: keep all
        )

        if selected_headers:
            if st.button("Process CSV"):
                result = process_and_filter_csv(
                    uploaded_file,
                    selected_headers,
                    input_delimiter=input_delimiter,
                    output_delimiter=output_delimiter
                )

                if result:
                    # Preview first 20 rows
                    df_preview = pd.read_csv(io.StringIO(result), delimiter=output_delimiter)
                    st.dataframe(df_preview.head(20))

                    st.download_button(
                        label="Download Filtered CSV",
                        data=result,
                        file_name="filtered_export.csv",
                        mime="text/csv"
                    )
        else:
            st.warning("Please select at least one column.")

    except Exception as e:
        st.error(f"Could not read headers from file: {e}")
