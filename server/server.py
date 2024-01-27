import json
import uuid

from pydantic import BaseModel
from fastapi import FastAPI
from remote_procedure_call.rabbit_remote_procedure_call import RabbitRPCFunctionCaller

app = FastAPI()

class TaskParam(BaseModel):
    text: str


@app.get('/')
def ping():
    return 'ok'


@app.post('/task')
def task(param: TaskParam):
    task_id = str(uuid.uuid4())
    rpc = RabbitRPCFunctionCaller(name_of_function='put_task', namespace='balancer')
    task = {
        'id': task_id,
        'dataSet': {
            'dataSplitter': {'fileName': 'balancer.py'},
            'link': param.text,
            'dataGetter': {'fileName': 'getter.py'},
            'dataSaver': {'fileName': 'saver.py'},
        },
        'algorithm': {'tasks': [
            {'fileName': 'algorithm.py'},
        ]}
    }
    rpc.call(json.dumps(task).encode())
    result = rpc.fetch_response()
    r = json.loads(result)
    return r['data']