# ----------------------------------------------------------------------------------------
# 
#
# ----------------------------------------------------------------------------------------

# Imports.  This template uses pyodbc
import json, logging, os
import pyodbc

from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    """ Get <thing> by ID.
        :param <param>: (int) the ID of the <thing>
        :param req: Passing the request
        :type req: HttpRequest
        :returns: Request
        :rtype: HttpResponse
    """

    id = req.route_params.get('id')
    logging.info(f'[START] GET /<thing>/{id}')

    #region #*----- Actions on Database                     ------------------------------
    #* generate prepared SQL statements, w/qmark placeholders preventing SQL injection
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
                    # qmark is only placeholder type pyodbc supports (no named queries)
                    cursor.execute("SELECT * FROM <table> WHERE <field> = ?", id)
                    columns = [column[0] for column in cursor.description]
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))

                except Exception as e:
                    logging.info(f'[ERROR] GET /<thing>, {e}')
                    return HttpResponse(u"Error: Failed to GET <thing>. Validate the <field> exists", status_code=500)

            logging.info(f'[SUCCESS] GET /<thing>/{id}')
            return HttpResponse(json.dumps(results), mimetype="application/json", status_code=200)

    except:
        logging.info(f'[ERROR] GET /<thing>/{id}')
        return HttpResponse(u"API Error", status_code=500)

    #endregion