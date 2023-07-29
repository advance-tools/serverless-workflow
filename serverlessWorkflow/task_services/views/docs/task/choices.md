## Description

The GET endpoint provides information about different choices and options available for various fields in the system. The response JSON contains the following key-value pairs:

- `status_choices`: A dictionary that maps status codes to their corresponding status labels.
- `immediate_input_type_choices`: A dictionary that maps immediate input type codes to their corresponding labels.
- `sub_task_input_type_choices`: A dictionary that maps sub-task input type codes to their corresponding labels.

## Endpoint URL

```
GET /api/choices/
```

## Request Parameters

This endpoint does not require any request parameters.

## Response

The response of the GET request will be a JSON object with the following structure:

```json
{
    "status_choices": {
        "0": "Pending",
        "1": "Completed",
        "2": "Errors"
    },
    "immediate_input_type_choices": {
        "0": "None",
        "1": "Current Response",
        "2": "Custom Input"
    },
    "sub_task_input_type_choices": {
        "0": "None",
        "1": "Current Response",
        "2": "Sub Task Response",
        "3": "Current And Sub Task Response",
        "4": "Custom Input"
    }
}
```

### Status Choices

The `status_choices` dictionary provides the available status options along with their corresponding codes. These status codes are used in various parts of the system to represent the current status of a task or process.

- `0`: "Pending" - The task or process is pending and has not been completed yet.
- `1`: "Completed" - The task or process has been successfully completed.
- `2`: "Errors" - The task or process encountered errors and could not be completed as expected.

### Immediate Input Type Choices

The `immediate_input_type_choices` dictionary provides the available options for immediate input types along with their corresponding codes. These options define how input is provided for immediate processing.

- `0`: "None" - No immediate input is required for processing.
- `1`: "Current Response" - The current response serves as the input for immediate processing.
- `2`: "Custom Input" - Custom input needs to be provided for immediate processing.

### Sub Task Input Type Choices

The `sub_task_input_type_choices` dictionary provides the available options for sub-task input types along with their corresponding codes. These options define how input is provided for sub-tasks.

- `0`: "None" - No input is required for sub-tasks.
- `1`: "Current Response" - The current response serves as the input for sub-tasks.
- `2`: "Sub Task Response" - The response from a sub-task is used as input for subsequent sub-tasks.
- `3`: "Current And Sub Task Response" - Both the current response and the response from a sub-task are used as input for subsequent sub-tasks.
- `4`: "Custom Input" - Custom input needs to be provided for sub-tasks.

## Example

**Request**

```
GET /api/choices/
```

**Response**

```json
{
    "status_choices": {
        "0": "Pending",
        "1": "Completed",
        "2": "Errors"
    },
    "immediate_input_type_choices": {
        "0": "None",
        "1": "Current Response",
        "2": "Custom Input"
    },
    "sub_task_input_type_choices": {
        "0": "None",
        "1": "Current Response",
        "2": "Sub Task Response",
        "3": "Current And Sub Task Response",
        "4": "Custom Input"
    }
}
```

## Status Codes

- `200 OK`: The request was successful, and the choices data is provided as a response.
- `500 Internal Server Error`: An error occurred on the server while processing the request.

## Notes

- This endpoint is read-only and does not modify any data in the system.
- The provided choices can be used in other API endpoints or client applications to ensure consistency and validity in user inputs.
- The status codes, immediate input type codes, and sub-task input type codes are integers for efficient representation and comparison in the system. However, the provided JSON response includes human-readable labels for better understanding.