import streamlit as st
import time

def processStep(status, message, function, *args, **kwargs):
    """Processes a single step of a pipeline, providing status updates.

    This function executes a given function with the provided arguments and
    displays status updates in a Streamlit application. It also measures
    and displays the execution time of the function.

    Args:
        status: The Streamlit status object.
        message: The message to display in the status update.
        function: The function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.
    """
    status_message = message
    st.info(icon='💬', body=status_message)
    status.update(label=status_message, state="running", expanded=True)
    start_time = time.time()
    result = function(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    if result:
        st.success(icon='🔥', body=f'{message} (Time taken: {elapsed_time:.2f} secs)')
    return result
