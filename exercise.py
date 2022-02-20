import json

import uvicorn
import logging
from fastapi import FastAPI, Request  
from fastapi.templating import Jinja2Templates 
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse

from config import *


app = FastAPI(title="anecdotes", description="receive a collected raw evidence",
              version="1.0.6", docs_url="/doc", redoc_url="/redoc")

# Add Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger = logging.getLogger("welcome")
logger.setLevel(logging.DEBUG)
STATIC_FOLDER = 'static' 

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/evidence", response_class=HTMLResponse)
async def evidence(request: Request):
     #axios.get("api/evidence",{evidence:[{},{},{} ...]})
     evidence_payload = json.loads(await request.body())['evidences']
     # evidence_payload = [ {
     # 'evidence_id': 1, 
     # 'evidence_data': [{'login_name': 'anecdotes-exercise',
     #                     'role': 'owner',
     #                     'user_details': {'updated_at': '2021-07-26T09:41:56Z', 'id': 120000, 'email':
     #                     'exercise@anecdotes.ai', 'first_name': 'anec', 'last_name': 'dotes'},
     #                     'security': {'mfa_enabled':True, 'mfa_enforced': True}}]
     #                     },
                         
     #                     {
     # 'evidence_id': 2, 
     # 'evidence_data': [{'login_name': 'anecdotes-exercise',
     #                     'role': 'owner',
     #                     'user_details': {'updated_at': '2021-07-26T09:41:56Z', 'id': 1000, 'email':
     #                     'exercise@andsdotes.ai', 'first_name': 'anec', 'last_name': 'dotes'},
     #                     'security': {'mfa_enabled':True, 'mfa_enforced': True}}]
     #                     }
     #                     ]
     new_config = {}

     #map config file
     for item in config:
          new_config[item['field']] = item
     
     data_list = []
     for evidence in evidence_payload:
          keys = evidence.keys()
          dict = {'evidence_id': '', 'data':[]}
          for key in keys:
               if key in new_config:
                    if 'type' in new_config[key] and new_config[key]['type'] == 'list':
                         for evidence_data in evidence[key]:
                              data = str(evidence_data).replace('{','')
                              data = data.replace('}','')
                              data = data.replace('\'','')
                              data = data.split(',')

                              for index in range(0,len(data)):
                                   item = data[index].split(': ')
                                   if len(item) == 2:
                                        item.pop(0)
                                        item = ':'.join(item)
                                        data[index] = item
                                   else:
                                        item.pop(0)
                                        item.pop(0)
                                        item = ':'.join(item)
                                        data[index] = item
                                        
                              dict['data'].append(data)

                    elif new_config[key]['title'] == 'id':
                         dict['evidence_id'] = evidence['evidence_id']
                         data_list.append(dict)
                              #creating html file with the animals:
               else:
                    print("key in not in map config")

     text = '''
     <html>
     <header>
          <table border=1 style='text-align:center'>
          <tr>
               <th>login_name</th>
               <th>role</th>
               <th>updated_at</th>
               <th>id</th>
               <th>email</th>
               <th>first_name</th>
               <th>last_name</th>
               <th>mfa_enabled</th>
               <th>mfa_enforced</th>
          </tr>
      '''

     table = ""


     for evidance_data in data_list:
          for index in range(0,len(evidance_data['data'])):
               sub_list = evidance_data['data'][index]
               table = table + "<tr>"
               for sub_index in range(0,len(sub_list)):
                    table = table + f"""<td>{sub_list[sub_index]}</td>"""
               table = table + "</tr>"

     text = text + table + '</table> </header> </html>'

     return text



@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()



# Offline Serving of API Docs 
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/html/swagger-ui-bundle.js",
        swagger_css_url="/html/swagger-ui.css",
    )


##
#   Background Process
##
counter = 0
@app.on_event("startup")
@repeat_every(seconds=300, logger=logger, wait_first=True)
def periodic():
    global counter
    print('background worker called ' + str(counter))
    counter += 1


# Startup
@app.on_event("startup")
def startup():
    print('running startup')


# Shutdown
@app.on_event("shutdown")
def shutdown():
    print('shutting down')

app.mount('/', StaticFiles(directory=STATIC_FOLDER), name=STATIC_FOLDER)
templates = Jinja2Templates(directory=STATIC_FOLDER)




if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)






