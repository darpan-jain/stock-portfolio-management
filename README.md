# Stock Portfolio Management

### Introduction

This project was created as a way to track my personal finances
and get daily updates about the changes in the portfolio value.
The entire project is configurable and uses the [NSETools](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi1i-WxjMbwAhWixDgGHXaXD8EQFjAAegQIBRAD&url=https%3A%2F%2Fnsetools.readthedocs.io%2Fen%2Flatest%2F&usg=AOvVaw0JIbThAoGW8WKVgxrNhnz0) and [BSETools](https://github.com/shahronak47/bsetools)
libraries to fetch the prices of a given set of stocks.
After this, the incoming data is analysed and an email update  is to sent to a user-defined
mailing list.

### Project structure
```
stock-portfolio-management
├── README.md
├── main.py
├── requirements.txt
├── run.sh
└── utils
    ├── configs
    │ └── sample_config.ini
    ├── data
    │ └── training
    │     └── training_experiments.ipynb
    ├── emails
    │ └── sample_email.html
    ├── get_news.py
    ├── get_stock_history.py
    ├── loggers.py
    ├── logging_setup.py
    ├── scrape.py
    └── send_email.py
```
- `run.sh` - shell script invoked by a crontab job
- `main.py` - the driver script which invokes the entire workflow
- `utils/scrape.py` - use the nse/bse libraries to fetch current data of a given stock, and analyse the data.
- `utils/send_email.py` - takes dataframes, prepares and sends email updates to the mailing list
- `loggers.py` - contains the loggers that can be used to log activities at various levels in the workflow

### Setup & Configuration

The project can be set up by first installing the required dependencies using
`pip3 install -r requirements.txt` in the main directory of the repository.

The configuration used by the workflow can be found under `utils/configs/config.ini`.
This file will have to be created by you before running the project.

The config contains the following parameters (refer to `sample_config.ini`)

- `csv path` - path to where the data for the stock prices is stored as a csv file
- `last update` - the date for when the last time the analysis was done. For first time users, set it to the present day's date.
- `sender email` - email address of the sender (your email address in your case)
- `sender pass` - a token provided by mailing services to allow the workflow to send emails on your behalf
- `receipients` - a comma separated list of email addresses
- `attachment name` - name of the attachment containing the updated stock info to be added in the email
- `debug` - a flag used for logging purposes
- `send` - a flag to send/not send email updates 
- `mode` - explained in the next section

### Modes

The workflow can operate in 3 modes based on the requirement. These can be set
under the `mode` param in the config file.

- `update` - add/delete stocks or change the number of shares
- `analyse` - only analyse and save the email locally, and not send it to the recipients
- `email` - analyse and send the email updates to the mailing list

### Sample Email Update
![Sample email update](https://github.com/darpan-jain/stock-portfolio-management/blob/main/utils/emails/sample_email.png)


