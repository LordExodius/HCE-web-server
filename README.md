# HCE Web Server

This repository contains the files necessary to deploy the webserver responsible for communicating with the [HCE Inference Server](https://github.com/LordExodius/HCE-inference-server) via Docker as part of this [thesis](https://github.com/LordExodius/ug-thesis).

## Usage
### Local Inference Server
If deploying to the same machine as the HCE Inference Server:
1. Deploy the webserver using `make deploy-shared`.

### Remote HCE Inference Server
If the HCE Inference Server is deployed to a remote server, uncomment and add the base url link to `TF_SERVING_ADDR` the `.env` file in the root directory.

1. Deploy the webserver using `make deploy`.

### Making Requests
Once the webserver is deployed, it will be available at http://localhost:8000. The port is defined by the local environment variable `HOST_REST_PORT` in `.env`.

By default, images can be sent to http://localhost:8000/image as a `POST` request, with a reponse in the form:

```json
{
  "numObjects": 1,
  "threshold": 0.5,
  "objects": [
    {
      "className": "bicycle",
      "score": 0.780103147,
      "y": 0.204752624,
      "x": 0.153316468,
      "height": 0.810077369,
      "width": 0.72613728
    },
  ]
}
```

You can access the API endpoint documentation at http://localhost:8000/docs.

### Configuration
If the model used in the HCE Inference Server changes, make sure to update the `MODEL_NAME` environment variable in `.env`.
