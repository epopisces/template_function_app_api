# ----------------------------------------------------------------------------------------
# 
#
# ----------------------------------------------------------------------------------------

# Imports.  This template uses pyodbc
import json, logging, os
import pyodbc

from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    """ Delete <thing> by ID.
        :param <param>: (type) the ID of the <thing>
        :type req: HttpRequest
        :returns: Request
        :rtype: HttpResponse
    """

    id = req.route_params.get('example_param')
    logging.info(f'[START] DELETE /<thing>/{id}')


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
                    cursor.execute("DELETE FROM <table> WHERE <field> = ?", id)
                    cursor.commit()

                except Exception as e:
                    logging.info(f'[ERROR] DELETE /<thing>, {e}')
                    return HttpResponse(u"Error: Failed to delete <thing>. Validate the <field> exists", status_code=500)

            logging.info(f'[SUCCESS] DELETE /<thing>/{id}')
            return HttpResponse(json.dumps(results), mimetype="application/json", status_code=200)

    except:
        logging.info(f'[ERROR] DELETE /<thing>/{id}')
        return HttpResponse(u"API Error", status_code=500)

    #endregion