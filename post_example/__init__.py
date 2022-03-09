# ----------------------------------------------------------------------------------------
# 
#
# ----------------------------------------------------------------------------------------

# imports.  Models are created from the OpenAPI spec as built by spotlight.io or similar

import models.models_py3 as models
import models.<thing>_enums as enum
import json, logging, os
import pyodbc # this template uses pyodbc to talk to the DB

from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    """ Create <thing>
        :param req: Passing the request, which must include a JSON format body
        :type req: HttpRequest
        :returns: Request
        :rtype: HttpResponse
    """
    
    logging.info(f'[START] POST /<thing>')
    body = req.get_json()

    #region #*----- Input Sanitization and Validation       ------------------------------
    #* if models correctly defined in OpenAPI spec, models used to sanitize/validate input
    #*------------------------------------------------------------------------------------
    
    try:    
        #? will fail if a mandatory field is missing
        new_<thing> = models.<Thing>New(**body)
    except TypeError as e:
        sanitized_error = "Error: " + e.args[0].split('() ')[1].replace('keyword-only argument', 'parameter')
        logging.info(f'[ERROR] POST /<thing>')
        return HttpResponse(sanitized_error, status_code=400)

    try:
        #? will fail if any parameter, key or value, is incorrect type
        if new_<thing>.validate():
            sanitized_error = 'Error: '
            for error in new_<thing>.validate():
                sanitized_error += error.args[0].replace('<Thing>New.','') + " "
            logging.info(f'[ERROR] POST /<thing>')
            return HttpResponse(sanitized_error, satus_code=400)
    except ValueError as e:
        sanitized_error = "Error: " + e.args[0].split('() ')[0].replace('literal for', 'parameter value, must be')
        logging.info(f'[ERROR] POST /<thing>')
        return HttpResponse(sanitized_error, satus_code=400)

    #? will fail when list of permitted values exists & param val provided doesn't match
    #? rmv if not using enums
    # TODO: improve this.  Awfully manual work, esp if enums are def for each attrib
    if new_<thing>.<attrib>:
        sanitized_error = 'Error: '
        if not any([True for val in enum.<Attrib> if val ==new_<thing>.<attrib>]):
            logging.info(f'[ERROR] POST /<thing>')
            sanitized_error += f"'{new_<thing>.<attrib>}' is an invalid value for param '<attrib>'.  Valid values: " + ', '.join([valid.value for valid in enum.<Attrib>])
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

            qmark_params = ''
            for key in body.keys():
                qmark_params += "?, "
            qmark_params = qmark_params[:-2]
            print(qmark_params)

            with conn.cursor() as cursor:
                try:
                    # qmark is only placeholder type pyodbc supports (no named queries)
                    prepared_statement = "INSERT INTO <Table> ({}) VALUES ({})".format(", ".join(body.keys()), qmark_params)
                    # TODO: check if the latter is the better method
                    #prepared_statement = "INSERT INTO <Table> ({}) VALUES ({})".format(", ".join([key + ' = ?' for key in body.keys() if key != "id"]))
                    cursor.execute(prepared_statement, [str(x) for x in body.values()])
                except Exception as e:
                    logging.info(f'[ERROR] POST /<thing>, {e}')
                    return HttpResponse(u"Error: Failed to create <thing>", status_code=500)
                conn.commit()

            logging.info(f'[SUCCESS] POST /<thing>/{id}')
            return HttpResponse(status_code=200)

    except:
        logging.info(f'[ERROR] POST /<thing>/{id}')
        return HttpResponse(u"Error: Failed to connect to the backend", status_code=500)

    #endregion