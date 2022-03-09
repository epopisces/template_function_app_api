# ----------------------------------------------------------------------------------------
# 
#
# ----------------------------------------------------------------------------------------

# Imports.  This template uses pyodbc
import json, logging, os
import pyodbc

from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    """ Get all <thing>.
        :param req: Passing the request
        :type req: HttpRequest
        :returns: Request
        :rtype: HttpResponse
    """

    logging.info(f'[START] GET /<thing>')

    #region #*----- Actions on Database                     ------------------------------
    #* generate prepared SQL statements
    #*------------------------------------------------------------------------------------
    try:
        results = []

        with pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server}"
            + ";Server="
            + os.environ["SQL_SERVER"]
            + ";PORT=1433;Database="
            + os.environ["SQL_DATABASE"]
            + ";Authentication=ActiveDirectoryMsi") as conn:

            with conn.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM <table>")
                    columns = [column[0] for column in cursor.description]
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))

                except Exception as e:
                    logging.info(f'[ERROR] GET /<thing>, {e}')
                    return HttpResponse(u"Error: Failed to get <thing>. Validate whether <field> is a valid entry", status_code=500)

            logging.info(f'[SUCCESS] GET /<thing>')
            return HttpResponse(json.dumps(results), mimetype="application/json", status_code=200)

    except:
        logging.info(f'[ERROR] GET /<thing>')
        return HttpResponse(u"API Error", status_code=500)

    #endregion