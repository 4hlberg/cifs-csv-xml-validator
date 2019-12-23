import os
import json
import logging

## Merge helper function
def dict_merger(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res

##Helper function for yielding on batch fetch
def stream_json(entities):
    logging.info("streaming started")
    try:
        first = True
        yield '['
        for i, row in enumerate(entities):
            if not first:
                yield ','
            else:
                first = False
            
            yield json.dumps(row)
        yield ']'
    except Exception as e:
        logging.error(f"Exiting with error : {e}")
    logging.info("stream ended")

