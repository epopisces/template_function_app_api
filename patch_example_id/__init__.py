# ----------------------------------------------------------------------------------------
# 
#
# ----------------------------------------------------------------------------------------

# imports.  Models are created from the OpenAPI spec as built by spotlight.io or similar
import enum
from multiprocessing.sharedctypes import Value
import models.models_py3 as models
import models.<thing>_enums as enum
import json, logging, os
import pyodbc # this template uses pyodbc to talk to the DB

from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    """ Update <thing> by ID.
        :param <param>: (int) the ID of the <thing>
        :param req: Passing the request, which must include a JSON format body
        :type req: HttpRequest
        :returns: Request
        :rtype: HttpResponse
    """

    body = req.get_json()
    body['id'] = req.route_params.get('id')
    logging.info(f'[START] PATCH /<thing>')

    #region #*----- Input Sanitization and Validation       ------------------------------
    #* if models correctly defined in OpenAPI spec, models used to sanitize/validate input
    #*------------------------------------------------------------------------------------
    
    try:    
        #? will fail if a mandatory field is missing
        upd_<thing> = models.<Thing>(**body)
    except TypeError as e:
        sanitized_error = "Error: " + e.args[0].split('() ')[1].replace('keyword-only argument', 'parameter')
        logging.info(f'[ERROR] PATCH /<thing>')
        return HttpResponse(sanitized_error, status_code=400)

    try:
        #? will fail if any parameter, key or value, is incorrect type
        if upd_<thing>.validate():
            sanitized_error = 'Error: '
            for error in upd_<thing>.validate():
                sanitized_error += error.args[0].replace('<Thing>.','') + " "
            logging.info(f'[ERROR] PATCH /<thing>')
            return HttpResponse(sanitized_error, satus_code=400)
    except ValueError as e:
        sanitized_error = "Error: " + e.args[0].split('() ')[0].replace('literal for', 'parameter value, must be')
        logging.info(f'[ERROR] PATCH /<thing>')
        return HttpResponse(sanitized_error, satus_code=400)

    #? will fail when list of permitted values exists & param val provided doesn't match
    #? rmv if not using enums
    # TODO: improve this.  Awfully manual work, esp if enums are def for each attrib
    if upd_<thing>.<attrib>:
        sanitized_error = 'Error: '
        if not any([True for val in enum.<Attrib> if val ==upd_<thing>.<attrib>]):
            logging.info(f'[ERROR] PATCH /<thing>')
            sanitized_error += f"'{upd_<thing>.<attrib>}' is an invalid value for param '<attrib>'.  Valid values: " + ', '.join([valid.value for valid in enum.<Attrib>])
            return HttpResponse(sanitized_error, satus_code=400)
    #endregion

    # The below is a test response, to test handling w/o actions on DB
    # return HttpResponse(json.dump(body), mimetype="application/json", status_code=200)

    #region #*----- Actions on Database                     ------------------------------
    #* generate prepared SQL statements, w/qmark placeholders preventing SQL injection
    #*------------------------------------------------------------------------------------

    try:    
        with pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server}"
            + ";Server="
            + os.environ["SQL_SERVER"]
            + ";PORT=1433;Database="
            + os.environ["SQL_DATABASE"]
            + ";Authentication=ActiveDirectoryMsi") as conn: # assumes MSI for the func app

            with conn.cursor() as cursor:
                try:
                    # qmark is only placeholder type pyodbc supports (no named queries)
                    prepared_statement = "UPDATE <Table> SET {} WHERE <field>=?".format(", ".join([key + ' = ?' for key in body.keys() if key != "id"]))
                    cursor.execute(prepared_statement, [str(x) for x in body.values()])
                except Exception as e:
                    logging.info(f'[ERROR] PATCH /<thing>, {e}')
                    return HttpResponse(u"Error: Failed to PATCH <thing>. Validate the <field> exists", status_code=500)
                conn.commit()

            logging.info(f'[SUCCESS] PATCH /<thing>/{id}')
            return HttpResponse(status_code=200)

    except:
        logging.info(f'[ERROR] PATCH /<thing>/{id}')
        return HttpResponse(u"Error: Failed to connect to the backend", status_code=500)

    #endregion