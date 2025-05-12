
# Project Name

## Prerequisites
- Python 3.11.9

## Installation

1. **Navigate to the project directory:**  

3. **Create a virtual environment:**  
   `python -m venv venv`

4. **Activate the virtual environment:**  
   - On Windows:  
     `venv\Scripts\activate`  
   - On macOS/Linux:  
     `source venv/bin/activate`

5. **Install the required packages:**  
   `pip install -r requirements.txt`

6. **Run testcases:**
	`pytest -cov`

## Running the Program

To run the program, execute the following command:  
`python src/main.py`

## Generated Datasets

### Price Reconciliation Report
- **Filename:** `{fund_name}_reconciliation_report.xlsx`  
  This report contains price reconciliation data for a single fund across various months, with the end-of-month (EOM) dates specified in a dedicated column.

  To include additional funds (N more), simply add the `{fund_name}` to the constant list in `main.py`.

### Best Performing Fund Report
- **Filename:** `best_performing_fund.xlsx`  
  This report highlights the best performing fund for each month, based on the rate of return.
